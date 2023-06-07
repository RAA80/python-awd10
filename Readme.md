## python-awd10 ##

Библиотека для работы с блоком управления коллекторным двигателем постоянного тока AWD10

### 1. Работа с консольной версией ###

        usage: awd-console [-h] --port [PORT] [--timeout [VALUE]] [--debug] [--scan]
                           [--unit [UNIT]]
                           [--echo | --reset | --state | --get KEY | --set KEY VALUE
                           | --move SPEED | --stop | --enrot | --result KEY]

        AWD10 command-line option

        optional arguments:
          -h, --help         show this help message and exit
          --port [PORT]      Set used port name
          --timeout [VALUE]  Set used timeout in second
          --debug            Print debug information

        Scanner:
          --scan             Scan available modules

        User:
          --unit [UNIT]      Set used AWD10 address
          --echo             Send ECHO request
          --reset            Send RESET request
          --state            Read AWD10 state
          --get KEY          Read config value. Possible KEY values: ['Address',
                             'BoardMode', 'CounterEMFShift', 'CurrentShift', 'D',
                             'DeadBand', 'Differential', 'DT', 'EMFCheckCounter',
                             'EMFCheckTime', 'FreqDirChange', 'Gain', 'I',
                             'Input1Shift', 'Input2Shift', 'LimitD', 'LimitI',
                             'LimitP', 'MaxCurrentLimit', 'MaxEncoderFreq',
                             'MaxFreqLimit', 'MaxPDMLimit', 'MinPDMLimit', 'P',
                             'PulsePerTurn', 'TrackModeFreq']
          --set KEY VALUE    Write config value. See --get for possible KEY values
          --move SPEED       Send MOVE command
          --stop             Send STOP request
          --enrot            Send ENROT request
          --result KEY       Read result value. Possible KEY values: ['ADC1', 'ADC2',
                             'PDM', 'Speed', 'Status']

Программа может работать в двух режимах: **Scanner** и **User**

#### Режим Scanner ####

В этом режиме происходит поиск активных модулей, подключенных к порту

Пример использования режима Scanner:

    awd-console --port COM5 --scan

Пример результата работы:

    Unit: 5 - OK

#### Режим User ####

Пример использования режима User:

-   Чтение регистра конфигурации режима работы блока управления

        awd-console --port COM5 --unit 5 --state

-   Посылка эхо-запроса

        awd-console --port COM5 --unit 5 --echo

-   Чтение значения параметра контроллера

        awd-console --port COM5 --unit 5 --get Address

-   Запись значения параметра в контроллер

        awd-console --port COM5 --unit 5 --set Address 5

-   Команда движения с постоянной скоростью 100 (или -100 для движения в обратную сторону)

        awd-console --port COM5 --unit 5 --move 100

-   Команда окончания выполнение режима

        awd-console --port COM5 --unit 5 --stop

-   Команда запуска режима слежения за внешним аналоговым сигналом (режим Сл)

        awd-console --port COM5 --unit 5 --enrot

### 2. Работа с графической версией ###

![AWD10 Controller 1](./doc/GUI_1.png)

### 3. Работа с симулятором AWD10 ###

    usage: awd-simulator [-h] --port [PORT] --unit [UNIT]

    AWD10 simulator command-line option

    optional arguments:
      -h, --help     show this help message and exit
      --port [PORT]  Set used port name
      --unit [UNIT]  Set used AWD10 address
