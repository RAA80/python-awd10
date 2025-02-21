#! /usr/bin/env python3

"""Реализация класса клиента для работы с блоком управления коллекторным
двигателем постоянного тока AWD10.
"""

from serial import Serial

from .protocol import Protocol


class AwdSerialClient(Protocol):
    """Класс для работы с блоком управления коллекторным двигателем
    постоянного тока AWD10.
    """

    def __init__(self, port: str, unit: int, timeout: float = 1.0) -> None:
        """Инициализация класса клиента с указанными параметрами."""

        super().__init__(unit)
        self.socket = Serial(port=port, timeout=timeout)    # default 9600-8-N-1

    def __del__(self) -> None:
        """Закрытие соединения с устройством при удалении объекта."""

        if self.socket.is_open:
            self.socket.close()

    def _bus_exchange(self, packet: bytes) -> bytes:
        """Обмен по интерфейсу."""

        self.socket.reset_input_buffer()
        self.socket.reset_output_buffer()

        self.socket.write(packet)
        return self.socket.read(size=8)


__all__ = ["AwdSerialClient"]
