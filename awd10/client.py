#! /usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import time
import struct
from functools import partial

_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())


# Коды команд управления
CMD_ECHO       = 0xF0   # «Эхо» запрос
CMD_EXEC_CMD   = 0x4B   # Команда выполнения действия
CMD_GET_PARAM  = 0x87   # Команда считывания значений параметров
CMD_GET_RESULT = 0x3C   # Команда получения текущего состояния параметров двигателя и блока управления
CMD_SET_PARAM  = 0x78   # Команда записи значений параметров

# Номера параметров для команды CMD_EXEC_CMD
CMD_ENROT  = 0x0B       # Начать выполнение режима слежения за внешним аналоговым сигналом (режим Сл)
CMD_RESET  = 0x09       # Позволяет установить настройки блока управления по умолчанию
CMD_SETROT = 0x08       # Позволяет задавать и получать параметры скорости, момента, направления вращения двигателя
CMD_STOP   = 0x0A       # Закончить выполнение режима


class Client(object):
    ''' Класс для работы с блоком управления коллекторным двигателем
        постоянного тока AWD10
    '''

    def __init__(self, transport, device, unit):
        self._transport = transport
        self._unit = unit
        self._device = device

    def __del__(self):
        if self._transport.is_open:
            self._transport.close()

    def __repr__(self):
        return "Client(transport={}, unit={})".format(self._transport, self._unit)

    def _verify(self, request, answer):
        if answer:
            if -sum(answer[:7]) & 0xFF != answer[7]:
                _logger.error("AwdProtocolError: unit %d crc error", answer[0])
            elif request[1] != answer[1]:
                _logger.error("AwdProtocolError: unit %d errorcode %02X", answer[0], answer[1])
            else:
                return True
        else:
            _logger.error("AwdProtocolError: unit %d has no answer", request[0])

    def _make_packet(self, command, param, data):
        packet = bytearray([self._unit,             # AWD10 address
                            command,                # Command code
                            param,                  # Parameter code
                            0x00,
                            (data & 0xFF00) >> 8,   # Data (High byte)
                            data & 0x00FF,          # Data (Low byte)
                            0x00,                   # Status
                            0x00])                  # Checksum
        packet[7] = -sum(packet) & 0xFF

        return packet

    def _wait_for_data(self, nbytes=None):
        size = 0
        more_data = False
        if self._transport.timeout is not None and self._transport.timeout != 0:
            condition = partial(lambda start, timeout:
                                (time.time() - start) <= timeout,
                                timeout=self._transport.timeout)
        else:
            condition = partial(lambda dummy1, dummy2: True, dummy2=None)
        start = time.time()
        while condition(start):
            avaialble = self._transport.in_waiting
            if (more_data and not avaialble) or (more_data and avaialble == size) or (nbytes == size):
                break
            if avaialble and avaialble != size:
                more_data = True
                size = avaialble
            time.sleep(0.01)
        return size

    def _bus_exchange(self, packet):
        self._transport.reset_input_buffer()
        self._transport.reset_output_buffer()

        self._transport.write(packet)
        size = self._wait_for_data(8)

        return self._transport.read(size)

    def _send_message(self, command, param, data):
        packet = self._make_packet(command, param, data)
        _logger.debug("Send frame = %s", list(packet))

        answer = self._bus_exchange(packet)
        try:
            answer = struct.unpack("!8B", answer)
        except struct.error as msg:
            _logger.error("AwdProtocolError: %s", msg)
            answer = None

        _logger.debug("Recv frame = %s", answer)
        return packet, answer

    def get_param(self, name):          # Таблица 7 из руководства по эксплуатации
        ''' Чтение значения параметра по заданному имени '''

        param = self._device["param"][name]['code']
        packet, answer = self._send_message(CMD_GET_PARAM, param, 0x0000)
        if self._verify(packet, answer):
            return (answer[4] << 8) + answer[5]

    def set_param(self, name, value):   # Таблица 7 из руководства по эксплуатации
        ''' Запись значения параметра по заданному имени '''

        _dev = self._device["param"][name]
        if value not in range(_dev['min'], _dev['max']+1):
            raise ValueError("Parameter '{}' out of range ({}, {}) value '{}'".
                             format(name, _dev['min'], _dev['max'], value))

        packet, answer = self._send_message(CMD_SET_PARAM, _dev['code'], int(value))
        return self._verify(packet, answer)

    def move(self, speed=0):
        ''' Команда движения с постоянной скоростью.
            Если скорость не указана или равна 0 происходит остановка движения
        '''

        data = int(speed & 0xFFFF)
        packet, answer = self._send_message(CMD_EXEC_CMD, CMD_SETROT, data)
        return self._verify(packet, answer)

    def state(self):
        ''' Чтение состояния '''

        packet, answer = self._send_message(CMD_GET_PARAM, 0x1C, 0x0000)
        if self._verify(packet, answer):
            return {'FB':          bool(answer[4]>>7 & 1),  # Управление обратной связью
                    'SkipLim':     bool(answer[4]>>6 & 1),  # Не использовать входы концевых выключателей
                    'LimDrop':     bool(answer[4]>>5 & 1),  # При срабатывании концевого выключателя не удерживать двигатель
                    'StopDrop':    bool(answer[4]>>4 & 1),  # При остановке вращения не удерживать двигатель
                    'IntrfEN':     bool(answer[4]>>3 & 1),  # Управлять разрешением режима «слежения» через интерфейс RS485
                    'IntrfVal':    bool(answer[4]>>2 & 1),  # Управлять величиной скорости или момента через интерфейс RS485
                    'IntrfDir':    bool(answer[4]>>1 & 1),  # Управлять направлением через интерфейс RS485
                    'SrcParam':    bool(answer[4]>>0 & 1),  # Выбор источника опорного сигнала
                    'SkipCV':      bool(answer[5]>>3 & 1),  # Способ обработки контрольной суммы в поле CS
                    'Mode':        answer[5] & 0x07,        # Режим платы
                    'StOverCur':   bool(answer[6]>>7 & 1),  # Индикатор токовой зашиты
                    'StMaxPWM':    bool(answer[6]>>6 & 1),  # Индикатор максимального управляющего сигнала (ШИМ)
                    'StDirFrwRev': bool(answer[6]>>5 & 1),  # Индикатор направления вращения
                    'StMotAct':    bool(answer[6]>>4 & 1),  # Признак вращения двигателя
                    'StInRev':     bool(answer[6]>>3 & 1),  # Состояние входа «движение назад» Rev
                    'StInFrw':     bool(answer[6]>>2 & 1),  # Состояние входа «движение вперед» Forw
                    'StLimRev':    bool(answer[6]>>1 & 1),  # Состояние входа «концевой выключатель «движение назад» LRev
                    'StLimFrw':    bool(answer[6]>>0 & 1)}  # Состояние входа «концевой выключатель «движение вперед» LFrw

    def reset(self):
        ''' Перезагрузка контроллера. Все параметры сбрасываются, движение прекращается '''

        packet, answer = self._send_message(CMD_EXEC_CMD, CMD_RESET, 0x0000)
        return self._verify(packet, answer)

    def echo(self):
        ''' Посылка Echo-запроса.
            Если устройство доступно возвратится True, иначе False
        '''

        packet, answer = self._send_message(CMD_ECHO, 0x0000, 0x0000)
        if self._verify(packet, answer):
            return answer[2:5] == (0x41, 0x57, 0x44)

    def stop(self):
        ''' Закончить выполнение режима '''

        packet, answer = self._send_message(CMD_EXEC_CMD, CMD_STOP, 0x0000)
        return self._verify(packet, answer)

    def enrot(self):
        ''' Включить режим слежения за внешним аналоговым сигналом '''

        packet, answer = self._send_message(CMD_EXEC_CMD, CMD_ENROT, 0x0000)
        return self._verify(packet, answer)

    def result(self, name):             # Таблица 9 из руководства по эксплуатации
        ''' Чтение значения текущего состояния параметров двигателя и блока управления '''

        param = self._device["result"][name]['code']
        packet, answer = self._send_message(CMD_GET_RESULT, param, 0x0000)
        if self._verify(packet, answer):
            return (answer[4] << 8) + answer[5]


__all__ = [ "Client" ]
