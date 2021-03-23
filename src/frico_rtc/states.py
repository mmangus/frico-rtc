from enum import Enum
from typing import TypeVar

from frico.bitstring import BitString


class Alarm1ConfigState(Enum):
    """Alarm state as defined on pg 12 of the datasheet (bit order flipped)"""

    ONCE_PER_SECOND = BitString("1111")
    SECONDS_MATCH = BitString("0111")
    MINUTES_SECONDS_MATCH = BitString("0011")
    HOURS_MINUTES_SECONDS_MATCH = BitString("0001")
    ALL_MATCH = BitString("0000")


class Alarm2ConfigState(Enum):
    """Alarm state as defined on pg 12 of the datasheet (bit order flipped)"""

    ONCE_PER_MINUTE = BitString("111")
    MINUTES_MATCH = BitString("011")
    HOURS_MINUTES_MATCH = BitString("001")
    ALL_MATCH = BitString("000")


class DayConfigState(Enum):
    """
    Represents whether an alarm is comparing the day of the week or the day of
    the month (date).
    """

    DAY_OF_MONTH = BitString(0)
    DAY_OF_WEEK = BitString(1)


class InterruptPinConfigState(Enum):
    SQUARE_WAVE = BitString("000")
    INTERRUPT_ON_ALARM1 = BitString("101")
    INTERRUPT_ON_ALARM2 = BitString("110")
    INTERRUPT_ON_BOTH = BitString("111")


class SquareWaveFrequencyConfigState(Enum):
    HZ_1 = BitString("00")
    HZ_1024 = BitString("01")
    HZ_4096 = BitString("10")
    HZ_8192 = BitString("11")


AlarmConfigState = TypeVar(
    "AlarmConfigState", Alarm1ConfigState, Alarm2ConfigState
)


DEFAULT_REGISTER_STATE = [BitString(0, fill=8)] * 0x13
