#! /usr/bin/env python3

"""Пример использования библиотеки."""

import logging
from time import sleep

from awd10.client import AwdSerialClient

logging.basicConfig(level=logging.INFO)


if __name__ == "__main__":
    client = AwdSerialClient(port="COM1", unit=5, timeout=0.2)

    print(f"Move: {client.move(speed=100)}")
    sleep(5)
    print(f"Move: {client.move(speed=0)}")

    # print(f'Get Address: {client.get_param("Address")}')  # Остальные названия параметров в файле 'device.py'
    # print(f'Set Address: {client.set_param("Address", 5)}')
    # print(f"Echo: {client.echo()}")
    # print(f"State: {client.state()}")
    # print(f'Result: {client.result("Status")}')
    # print(f"Stop: {client.stop()}")
    # print(f"Reset: {client.reset()}")
