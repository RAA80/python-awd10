#! /usr/bin/env python3

"""Реализация класса клиента для работы с блоком управления коллекторным
двигателем постоянного тока AWD10.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from awd10.protocol import Protocol

if TYPE_CHECKING:
    from serial import Serial


class AwdSerialClient(Protocol):
    """Класс для работы с блоком управления коллекторным двигателем
    постоянного тока AWD10.
    """

    def __init__(self, transport: Serial, unit: int) -> None:
        """Инициализация класса клиента с указанными параметрами."""

        super().__init__(unit)
        self.transport = transport

    def __del__(self) -> None:
        """Закрытие соединения с устройством при удалении объекта."""

        if self.transport.is_open:
            self.transport.close()

    def _bus_exchange(self, packet: bytes) -> bytes:
        """Обмен по интерфейсу."""

        self.transport.reset_input_buffer()
        self.transport.reset_output_buffer()

        self.transport.write(packet)
        return self.transport.read(size=8)


__all__ = ["AwdSerialClient"]
