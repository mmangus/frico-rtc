# Frico RTCs

Interface to the Dallas/Maxim DS-series RTC devices using the
[Frico](https://github.com/mmangus/frico) framework. Currently
supports the DS3231/MAX31328, with the DS1307 and DS1337 to come, 
among others.

## Installation
You can download and install the package via pip:
```shell
python3 -m pip install frico-rtc
```

To contribute, use the provided Makefile to set up a development
environment:
```shell
git clone git@github.com:mmangus/frico-rtc.git &&\
cd frico-rtc &&\
make
```

Run `make test` to validate changes (or use the commit hooks).

## Usage
```python
from datetime import datetime
from frico_rtc.devices import DS3231
rtc = DS3231()
# read time from RTC
print(rtc.time)  
# set time on RTC
rtc.time = datetime.now()
# check alarm config
print(rtc.alarm1config)
```
