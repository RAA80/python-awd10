## python-awd10 ##

Библиотека для работы с блоком управления коллекторным двигателем постоянного тока AWD10

### 1. Работа с консольной версией ###

Программа может работать в двух режимах

- Режим **Scanner**
- Режим **User**

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

##### Режим Scanner #####

Пример использования режима Scanner:

	awd-console --port COM5 --scan

Пример использования режима Scanner с выводом отладочной информации:

	awd-console --port COM5 --scan --debug

##### Режим User #####

Пример использования режима User:

	awd-console --port COM5 --unit 5 --move 100
	awd-console --port COM5 --unit 5 --get Address
	awd-console --port COM5 --unit 5 --set Address 5
	awd-console --port COM5 --unit 5 --echo
	awd-console --port COM5 --unit 5 --state

Пример использования режима User с выводом отладочной информации:

	awd-console --port COM5 --unit 5 --move 100 --debug

### 2. Работа с графической версией ###

![AWD10 Controller 1](./doc/GUI_1.png)

### 3. Работа с симулятором AWD10 ###

	usage: awd-simulator [-h] --port [PORT] --unit [UNIT]

	AWD10 simulator command-line option

	optional arguments:
	  -h, --help     show this help message and exit
	  --port [PORT]  Set used port name
	  --unit [UNIT]  Set used AWD10 address
