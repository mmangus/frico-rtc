from abc import abstractmethod
from states import Iterable, TYPE_CHECKING

from frico.blocks import RegisterBlock, TimekeepingRegisterBlock

from .parsers import (
    HourParser,
    MinuteParser,
    # DayOfWeekParser,
    DayOfMonthParser,
    SecondParser,
    MonthParser,
    YearParser,
    Alarm1ConfigParser,
    DayConfigParser,
    Alarm2ConfigParser,
    TemperatureParser,
    FlagParser,
)
from .states import (
    Alarm1ConfigState,
    Alarm2ConfigState,
    DayConfigState,
    SquareWaveFrequencyConfigState,
)

if TYPE_CHECKING:
    from frico.device import I2CDevice
    from frico.state_types import RegisterState

class Clock(TimekeepingRegisterBlock):
    """
    Descriptor for getting/setting clock state to/from datetime objects.

    This format is shared by the DS3231, DS1307, and DS1337 (and probably
    others).
    """
    second = SecondParser(0x00)
    minute = MinuteParser(0x01)
    hour = HourParser(0x02)
    # day_of_week = DayOfWeekParser(0x03)
    day_of_month = DayOfMonthParser(0x04)
    month = MonthParser(0x05)
    year = YearParser(slice(0x05, 0x07))


class Alarm1(TimekeepingRegisterBlock):
    """
    Descriptor for getting/setting Alarm1 state to/from datetime objects.

    This format is shared by the DS3231 and DS1337 (and probably others).
    """
    second = SecondParser(0x07)
    minute = MinuteParser(0x08)
    hour = HourParser(0x09)
    # day_of_week = DayOfWeekParser(0x0A)
    day_of_month = DayOfMonthParser(0x0A)


class Alarm2(TimekeepingRegisterBlock):
    """
    Descriptor for getting/setting Alarm2 state to/from datetime objects.

    This format is shared by the DS3231 and DS1337 (and probably others).
    """
    minute = MinuteParser(0x0B)
    hour = HourParser(0x0C)
    # day_of_week = DayOfWeekParser(0x0D)
    day_of_month = DayOfMonthParser(0x0D)


class Alarm1Config(RegisterBlock[Iterable[Alarm1ConfigState, DayConfigState]]):
    """
    Descriptor for reading/writing Alarm 1 state from ConfigState enums.

    This format is shared by the DS3231 and DS1337 (and probably others).
    """
    alarm_config = Alarm1ConfigParser(slice(0x07, 0x0B))
    day_config = DayConfigParser(0x0A)

    def _prepare_update(
            self,
            value: Iterable[Alarm1ConfigState, DayConfigState]
    ) -> None:
        self.alarm_config, self.day_config = value

    def _value(self) -> Iterable[Alarm1ConfigState, DayConfigState]:
        return self.alarm_config, self.day_config


class Alarm2Config(RegisterBlock[Iterable[Alarm2ConfigState, DayConfigState]]):
    """
    Descriptor for reading/writing Alarm 2 state from ConfigState enums.

    This format is shared by the DS3231 and DS1337 (and probably others).
    """
    alarm_config = Alarm2ConfigParser(slice(0x0B, 0x0D))
    day_config = DayConfigParser(0x0D)

    def _prepare_update(
            self,
            value: Iterable[Alarm2ConfigState, DayConfigState]
    ) -> None:
        self.alarm_config, self.day_config = value


    def _value(self) -> Iterable[Alarm2ConfigState, DayConfigState]:
        return self.alarm_config, self.day_config


class Temperature(RegisterBlock[float]):
    """
    Descriptor to get the temperature value (used for TCXO calibration on the
    DS3231).
    """
    temperature = TemperatureParser(slice(0x11, 0x13))

    def _prepare_update(self, value: float) -> None:
        raise AttributeError("Temperature is read-only")

    def _value(self) -> float:
        return self.temperature


class ControlRegisterBlock(RegisterBlock[bool]):
    """
    Base class for boolean control flags.
    """
    @property
    @abstractmethod
    def flag(self) -> FlagParser:
        pass

    @flag.setter
    def flag(self, value: bool) -> None:
        pass

    def _prepare_update(
            self,
            value: bool
    ) -> None:
        self.flag = value


class OscillatorEnable(ControlRegisterBlock):
    # TODO
    pass


class SquareWaveConfig(RegisterBlock[Iterable[SquareWaveFrequencyConfigState, bool]]):
    # TODO
    pass
