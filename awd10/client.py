#! /usr/bin/env python3

"""Реализация класса клиента для работы с блоком управления коллекторным
двигателем постоянного тока AWD10.
"""

import logging

from serial import Serial

_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())


# Коды команд управления (таблица 6 документации)
CMD_ECHO = 0xF0
CMD_EXEC_CMD = 0x4B
CMD_GET_PARAM = 0x87
CMD_GET_RESULT = 0x3C
CMD_SET_PARAM = 0x78

# Номера параметров для команды CMD_EXEC_CMD (таблица 8 документации)
CMD_ENROT = 0x0B
CMD_RESET = 0x09
CMD_SETROT = 0x08
CMD_STOP = 0x0A


class AwdProtocolError(Exception):
    pass


class Client:
    """Класс для работы с блоком управления коллекторным двигателем
    постоянного тока AWD10.
    """

    def __init__(self, port: str, unit: int,
                       device: dict, timeout: float = 1.0) -> None:
        """Инициализация класса клиента с указанными параметрами."""

        self.socket = Serial(port=port, timeout=timeout)
        self.port = port
        self.unit = unit
        self.device = device

    def __del__(self) -> None:
        """Закрытие соединения с устройством при удалении объекта."""

        if self.socket.is_open:
            self.socket.close()

    def __repr__(self) -> str:
        """Строковое представление объекта."""

        return f"Client(port={self.port}, unit={self.unit})"

    @staticmethod
    def _error_check(request: bytes, answer: bytes) -> bool:
        """Проверка возвращаемого значения на ошибку."""

        if len(answer) < 8:
            msg = f"unit {request[0]} received incomplete answer"
            raise AwdProtocolError(msg)
        if -sum(answer[:7]) & 0xFF != answer[7]:
            msg = f"unit {answer[0]} crc error"
            raise AwdProtocolError(msg)
        if request[1] != answer[1]:
            msg = f"unit {answer[0]} error code {answer[1]:02X}"
            raise AwdProtocolError(msg)
        return True

    def _make_packet(self, command: int, param: int, data: int) -> bytes:
        """Формирование пакета для записи."""

        packet = [self.unit, command, param, 0, *data.to_bytes(2, "big"), 0, 0]
        packet[7] = -sum(packet) & 0xFF

        return bytes(packet)

    def _bus_exchange(self, packet: bytes) -> bytes:
        """Обмен по интерфейсу."""

        self.socket.reset_input_buffer()
        self.socket.reset_output_buffer()

        self.socket.write(packet)
        return self.socket.read(size=8)

    def _send_message(self, command: int, param: int, data: int) -> bytes:
        """Послать команду в устройство."""

        packet = self._make_packet(command, param, data)
        _logger.debug("Send frame = %s", list(packet))

        answer = self._bus_exchange(packet)
        _logger.debug("Recv frame = %s", list(answer))

        self._error_check(packet, answer)
        return answer

    def get_param(self, name: str) -> int:                  # Таблица 7 документации
        """Чтение значения параметра по заданному имени."""

        return self._get_value("param", name, CMD_GET_PARAM)

    def set_param(self, name: str, value: int) -> bool:     # Таблица 7 документации
        """Запись значения параметра по заданному имени."""

        dev = self.device["param"][name]
        if value not in range(dev["min"], dev["max"] + 1):
            msg = f"An '{name}' value of '{value}' is out of range"
            raise AwdProtocolError(msg)

        return bool(self._send_message(CMD_SET_PARAM, dev["code"], value))

    def move(self, speed: int = 0) -> bool:
        """Движение с постоянной скоростью. Знак скорости определяет направление."""

        return bool(self._send_message(CMD_EXEC_CMD, CMD_SETROT, speed & 0xFFFF))

    def state(self) -> dict:        # п.2.5.4.4 и 2.5.4.5 документации
        """Чтение состояния флагов режима работы платы."""

        answer = self._send_message(CMD_GET_PARAM, 0x1C, 0x0000)
        return {"FB":          bool(answer[4] >> 7 & 1),
                "SkipLim":     bool(answer[4] >> 6 & 1),
                "LimDrop":     bool(answer[4] >> 5 & 1),
                "StopDrop":    bool(answer[4] >> 4 & 1),
                "IntrfEN":     bool(answer[4] >> 3 & 1),
                "IntrfVal":    bool(answer[4] >> 2 & 1),
                "IntrfDir":    bool(answer[4] >> 1 & 1),
                "SrcParam":    bool(answer[4] >> 0 & 1),
                "SkipCV":      bool(answer[5] >> 3 & 1),
                "Mode":        answer[5] & 0x07,
                "StOverCur":   bool(answer[6] >> 7 & 1),
                "StMaxPWM":    bool(answer[6] >> 6 & 1),
                "StDirFrwRev": bool(answer[6] >> 5 & 1),
                "StMotAct":    bool(answer[6] >> 4 & 1),
                "StInRev":     bool(answer[6] >> 3 & 1),
                "StInFrw":     bool(answer[6] >> 2 & 1),
                "StLimRev":    bool(answer[6] >> 1 & 1),
                "StLimFrw":    bool(answer[6] >> 0 & 1)}

    def reset(self) -> bool:
        """Все параметры сбрасываются, движение прекращается."""

        return bool(self._send_message(CMD_EXEC_CMD, CMD_RESET, 0x0000))

    def echo(self) -> bool:
        """Посылка Echo-запроса. Если устройство доступно возвратится True."""

        answer = self._send_message(CMD_ECHO, 0x0000, 0x0000)
        return tuple(answer[2:5]) == (0x41, 0x57, 0x44)

    def stop(self) -> bool:
        """Закончить выполнение режима."""

        return bool(self._send_message(CMD_EXEC_CMD, CMD_STOP, 0x0000))

    def enrot(self) -> bool:
        """Включить режим слежения за внешним аналоговым сигналом."""

        return bool(self._send_message(CMD_EXEC_CMD, CMD_ENROT, 0x0000))

    def result(self, name: str) -> int:             # Таблица 9 документации
        """Чтение параметров состояния двигателя и блока управления."""

        return self._get_value("result", name, CMD_GET_RESULT)

    def _get_value(self, arg: str, name: str, cmd: int) -> int:
        """Чтение текущего параметра или состояния двигателя."""

        param = self.device[arg][name]["code"]
        answer = self._send_message(cmd, param, 0)
        return answer[4] << 8 | answer[5]


__all__ = ["Client"]
