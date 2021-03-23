from frico.devices import I2CDevice

from .blocks import (
    Alarm1,
    Alarm1Config,
    Alarm2,
    Alarm2Config,
    Clock,
    Temperature,
)


class DS3231(I2CDevice):
    """
    Interface to the DS3231 I2C RTC using SMBus.

    Datasheet: https://datasheets.maximintegrated.com/en/ds/DS3231.pdf
    """

    I2C_ADDRESS = 0x68  # I2C device address for DS3231
    I2C_READ_START = 0x00
    I2C_READ_LEN = 0x13  # data repeats after 0x12, so only read 0x13 bytes

    # See page 11 of the datasheet for register layout details
    clock = Clock()
    alarm1 = Alarm1()
    alarm1config = Alarm1Config()
    alarm2 = Alarm2()
    alarm2config = Alarm2Config()
    temperature = Temperature()

    def __str__(self) -> str:
        return str(self.clock)

    def __repr__(self) -> str:
        return f"DS3231({self.bus})"
