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
        return ("Client(transport={}, unit={})".format(self._transport,
                                                       self._unit))

    def _verify(self, request, answer):
        if answer:
            error = 0 if request[1] == answer[1] else answer[1]
            crc = -sum(answer[0:7]) & 0xFF == answer[7]

            if crc and (not error):
                return True
            elif not crc:
                _logger.error("AwdProtocolError: unit {} crc error".
                                    format(answer[0]))
            elif error:
                _logger.error("AwdProtocolError: unit {} errorcode {:X}".
                                    format(answer[0], error))
        else:
            _logger.error("AwdProtocolError: unit {} has no answer".
                           format(request[0]))

    def _make_packet(self, request):
        packet = bytearray([self._unit,                         # AWD10 address
                            request['command'],                 # Command code
                            request['param'],                   # Parameter code
                            0x00,
                            (request['data'] & 0xFF00) >> 8,    # Data (High byte)
                            request['data'] & 0x00FF,           # Data (Low byte)
                            0x00,                               # Status
                            0x00])                              # Checksum
        packet[7] = -sum(packet) & 0xFF

        return packet

    def _in_waiting(self):
        in_waiting = ("in_waiting" if hasattr(
            self._transport, "in_waiting") else "inWaiting")

        if in_waiting == "in_waiting":
            waitingbytes = getattr(self._transport, in_waiting)
        else:
            waitingbytes = getattr(self._transport, in_waiting)()
        return waitingbytes

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
            avaialble = self._in_waiting()
            if (more_data and not avaialble) or (more_data and avaialble == size) or (nbytes == size):
                break
            if avaialble and avaialble != size:
                more_data = True
                size = avaialble
            time.sleep(0.01)
        return size

    def _getPingPong(self, request):
        self._transport.reset_input_buffer()
        self._transport.reset_output_buffer()

        packet = self._make_packet(request)
        writed = self._transport.write(packet)

        size = self._wait_for_data(8)
        answer = self._transport.read(size)
        try:
            answer = struct.unpack("!8B", answer)
        except struct.error as msg:
            _logger.error("AwdProtocolError: {}".format(msg))
            answer = None

        _logger.debug("Send frame = {}".format(list(bytearray(packet))))
        _logger.debug("Recv frame = {}".format(answer))

        return packet, answer

    def getParam(self, name):           # Таблица 7 из руководства по эксплуатации
        ''' Чтение значения параметра по заданному имени '''

        request = {'command': CMD_GET_PARAM,
                   'param':   self._device["param"][name]['code'],
                   'data':    0x0000}
        packet, answer = self._getPingPong(request)

        if self._verify(packet, answer):
            return (answer[4] << 8) + answer[5]

    def setParam(self, name, value):    # Таблица 7 из руководства по эксплуатации
        ''' Запись значения параметра по заданному имени '''

        _dev = self._device["param"][name]

        if value < _dev['min'] or value > _dev['max']:
            raise ValueError("Parameter [{}] out of range ({}, {})".
                             format(name, _dev['min'], _dev['max']))

        request = {'command': CMD_SET_PARAM,
                   'param':   _dev['code'],
                   'data':    int(value)}
        packet, answer = self._getPingPong(request)

        return self._verify(packet, answer)

    def move(self, speed=0):
        ''' Команда движения с постоянной скоростью.
            Если скорость не указана или равна 0 происходит остановка движения
        '''

        request = {'command': CMD_EXEC_CMD,
                   'param':   CMD_SETROT,
                   'data':    int(speed)}
        packet, answer = self._getPingPong(request)

        return self._verify(packet, answer)

    def state(self):
        ''' Чтение состояния '''

        request = {'command': CMD_GET_PARAM,
                   'param':   0x1C,
                   'data':    0x0000}
        packet, answer = self._getPingPong(request)

        if self._verify(packet, answer):
            return {'FB':          bool(answer[4] & (1<<7)),    # Управление обратной связью
                    'SkipLim':     bool(answer[4] & (1<<6)),    # Не использовать входы концевых выключателей
                    'LimDrop':     bool(answer[4] & (1<<5)),    # При срабатывании концевого выключателя не удерживать двигатель
                    'StopDrop':    bool(answer[4] & (1<<4)),    # При остановке вращения не удерживать двигатель
                    'IntrfEN':     bool(answer[4] & (1<<3)),    # Управлять разрешением режима «слежения» через интерфейс RS485
                    'IntrfVal':    bool(answer[4] & (1<<2)),    # Управлять величиной скорости или момента через интерфейс RS485
                    'IntrfDir':    bool(answer[4] & (1<<1)),    # Управлять направлением через интерфейс RS485
                    'SrcParam':    bool(answer[4] & (1<<0)),    # Выбор источника опорного сигнала
                    'SkipCV':      bool(answer[5] & (1<<3)),    # Способ обработки контрольной суммы в поле CS
                    'Mode':        answer[5] & 0x07,            # Режим платы
                    'StOverCur':   bool(answer[6] & (1<<7)),    # Индикатор токовой зашиты
                    'StMaxPWM':    bool(answer[6] & (1<<6)),    # Индикатор максимального управляющего сигнала (ШИМ)
                    'StDirFrwRev': bool(answer[6] & (1<<5)),    # Индикатор направления вращения
                    'StMotAct':    bool(answer[6] & (1<<4)),    # Признак вращения двигателя
                    'StInRev':     bool(answer[6] & (1<<3)),    # Состояние входа «движение назад» Rev
                    'StInFrw':     bool(answer[6] & (1<<2)),    # Состояние входа «движение вперед» Forw
                    'StLimRev':    bool(answer[6] & (1<<1)),    # Состояние входа «концевой выключатель «движение назад» LRev
                    'StLimFrw':    bool(answer[6] & (1<<0))}    # Состояние входа «концевой выключатель «движение вперед» LFrw

    def reset(self):
        ''' Перезагрузка контроллера. Все параметры сбрасываются, движение прекращается '''

        request = {'command': CMD_EXEC_CMD,
                   'param':   CMD_RESET,
                   'data':    0x0000}
        packet, answer = self._getPingPong(request)

        return self._verify(packet, answer)

    def echo(self):
        ''' Посылка Echo-запроса.
            Если устройство доступно возвратится True, иначе False
        '''

        request = {'command': CMD_ECHO,
                   'param':   0x0000,
                   'data':    0x0000}
        packet, answer = self._getPingPong(request)

        if self._verify(packet, answer):
            return answer[2:5] == (0x41, 0x57, 0x44)

    def stop(self):
        ''' Закончить выполнение режима '''

        request = {'command': CMD_EXEC_CMD,
                   'param':   CMD_STOP,
                   'data':    0x0000}
        packet, answer = self._getPingPong(request)

        return self._verify(packet, answer)

    def enrot(self):
        ''' Включить режим слежения за внешним аналоговым сигналом '''

        request = {'command': CMD_EXEC_CMD,
                   'param':   CMD_ENROT,
                   'data':    0x0000}
        packet, answer = self._getPingPong(request)

        return self._verify(packet, answer)

    def result(self, name):             # Таблица 9 из руководства по эксплуатации
        ''' Чтение значения текущего состояния параметров двигателя и блока управления '''

        request = {'command': CMD_GET_RESULT,
                   'param':   self._device["result"][name]['code'],
                   'data':    0x0000}
        packet, answer = self._getPingPong(request)

        if self._verify(packet, answer):
            return (answer[4] << 8) + answer[5]


__all__ = [ "Client" ]
