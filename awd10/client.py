#! /usr/bin/env python3

"""Реализация класса клиента для работы с блоком управления коллекторным
двигателем постоянного тока AWD10.
"""

from __future__ import annotations

from socket import AF_INET, SOCK_STREAM, socket

from serial import Serial

from awd10.protocol import Protocol


class AwdBaseTransport:
    """Базовый класс транспорта."""

    def _bus_exchange(self, packet: bytes) -> bytes:
        """Обмен по интерфейсу."""

        raise NotImplementedError


class AwdSerialTransport(AwdBaseTransport):
    """Класс транспорта для работы через последовательный порт."""

    def __init__(self, address: str, timeout: float = 1.0) -> None:
        """Инициализация класса с указанными параметрами."""

        self._socket = Serial(port=address, timeout=timeout)    # default 9600-8-N-1

    def __del__(self) -> None:
        """Закрытие соединения с устройством при удалении объекта."""

        if hasattr(self, "_socket") and self._socket.is_open:
            self._socket.close()

    def _bus_exchange(self, packet: bytes) -> bytes:
        """Обмен по интерфейсу."""

        self._socket.reset_input_buffer()
        self._socket.reset_output_buffer()

        self._socket.write(packet)
        return self._socket.read(size=8)


class AwdTcpTransport(AwdBaseTransport):
    """Класс транспорта для работы через TCP/IP."""

    def __init__(self, address: str, timeout: float = 1.0) -> None:
        """Инициализация класса с указанными параметрами."""

        ip, tcp_port = address.split(":")
        self._socket = socket(AF_INET, SOCK_STREAM)
        self._socket.settimeout(timeout)
        self._socket.connect((ip, int(tcp_port)))

    def __del__(self) -> None:
        """Закрытие соединения с устройством при удалении объекта."""

        if self._socket:
            self._socket.close()

    def _bus_exchange(self, packet: bytes) -> bytes:
        """Обмен по интерфейсу."""

        self._socket.sendall(packet)
        return self._socket.recv(8)


class AwdDevice(Protocol):
    """Класс клиента для работы с блоком управления AWD10."""

    def __init__(self, transport: AwdBaseTransport, unit: int) -> None:
        """Инициализация класса клиента с указанными параметрами."""

        super().__init__(unit)
        self._transport = transport

    def _bus_exchange(self, packet: bytes) -> bytes:
        """Обмен по интерфейсу."""

        return self._transport._bus_exchange(packet)


__all__ = ["AwdDevice", "AwdSerialTransport", "AwdTcpTransport"]
