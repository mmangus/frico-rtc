from abc import abstractmethod
from typing import List, NoReturn, Type

from frico.bitstring import BitString
from frico.parsers import BCDParser, FlagParser, RegisterParser
from frico.typing import RegisterState

from .states import (
    Alarm1ConfigState,
    Alarm2ConfigState,
    AlarmConfigState,
    DayConfigState,
)


class SecondParser(BCDParser):
    """Parser for registers representing seconds on DS-series RTCs."""

    bcd_bounds = ((1, 4), (4, 8))


class MinuteParser(BCDParser):
    """Parser for registers representing minutes on DS-series RTCs."""

    bcd_bounds = ((1, 4), (4, 8))


class DayOfMonthParser(BCDParser):
    """Parser for registers representing day of the month on DS-series RTCs."""

    bcd_bounds = ((2, 4), (4, 8))


class DayOfWeekParser(BCDParser):
    """Parser for registers representing day of the week on DS-series RTCs."""

    bcd_bounds = ((5, 8),)


class MonthParser(BCDParser):
    """Parser for registers representing the month on DS-series RTCs."""

    bcd_bounds = ((3, 4), (4, 8))


class HourParser(RegisterParser[int]):
    """
    Parser for registers representing hours on DS-series RTCs.

    This requires two different calculations depending on whether the 24-hour
    mode bit is set.
    """

    def _value(self) -> int:
        if self._local_bytes[0][1]:  # 12h mode
            hours = self._local_bytes[0].decode_bcd((3, 4), (4, 8))
            if self._local_bytes[0][2]:
                hours += 12
            return hours
        # if 20 hour bit is set, 2; if 10 hour bit is set, 1; else 0
        hour_tens = self._local_bytes[0][2] * 2 + self._local_bytes[0][3]
        hour_ones = self._local_bytes[0][4:]
        return 10 * hour_tens + hour_ones

    def _prepare_update(self, value: int) -> RegisterState:
        new_bitstring = BitString.encode_bcd(value, (3, 4))
        new_state = [self._local_bytes[0].replace(1, new_bitstring)]
        # FIXME what is gonna happen to 12h mode?
        return new_state


class YearParser(RegisterParser[int]):
    """
    Parser for registers representing the year on DS-series RTCs.

    Century (+100 or not) is represented with 1 bit in the first register and
    the year from 00-99 is simple BCD in the second register.
    """

    def _value(self) -> int:
        return (
            2000
            + self._local_bytes[0][0] * 100
            + self._local_bytes[1].decode_bcd((0, 4), (4, 8))
        )

    def _prepare_update(self, value: int) -> RegisterState:
        if value >= 2200 or value < 2000:
            # technically I guess the RTC just doesn't care *which*
            # millennium it is, but this seems good enough...
            raise ValueError(f"Year {value} out of range for RTC.")
        value -= 2000  # RTC only stores the last 3 digits
        new_state: List[BitString] = []
        if value >= 100:  # Adjust the century bit as necessary
            new_state.append(self._local_bytes[0].replace(0, BitString("1")))
            value -= 100
        else:
            new_state.append(self._local_bytes[0].replace(0, BitString("0")))
        new_state.append(BitString.encode_bcd(value))
        return new_state


class TemperatureParser(RegisterParser[float]):
    """
    Parser for registers representing the Celsius temperature on the DS3231.

    Twos-compliment signed integer in the first register with a fractional part
    stored as 2 bits in units of 0.25 degrees in the second register.
    """

    def _value(self) -> float:
        integer_part = self._local_bytes[0].decode_bcd((1, 8))
        if self._local_bytes[0][0]:  # sign bit set, convert 2s compliment
            # xor the bits with 255 (0b11111111) to invert, then subtract 1
            integer_part = (integer_part ^ 255) - 1
        fractional_part = 0.25 * self._local_bytes[1].decode_bcd((0, 2))
        return integer_part + fractional_part

    def _prepare_update(self, value: float) -> NoReturn:
        raise AttributeError("Temperature is read-only")


class DayConfigParser(RegisterParser[DayConfigState]):
    def _value(self) -> DayConfigState:
        return DayConfigState(self._local_bytes[0][0])

    def _prepare_update(self, value: DayConfigState) -> RegisterState:
        if not isinstance(value, DayConfigState):
            raise ValueError(
                f"Invalid config: expected a DayConfigState instance but got "
                f"{value}"
            )
        new_state = [self._local_bytes[0].replace(0, value.value)]
        return new_state


class AlarmConfigParser(RegisterParser[AlarmConfigState]):
    """
    Parser for Alarm configuration mask stored in the first bits of 0x07-0x0xA
    and 0x0B-0x0D
    """

    @property
    @abstractmethod
    def config_cls(self) -> Type[AlarmConfigState]:
        pass

    def _value(self) -> AlarmConfigState:
        # read the first bit of each register to get the config mask
        mask = BitString.concat(*(byte[0] for byte in self._local_bytes))
        return self.config_cls(mask)

    def _prepare_update(self, value: AlarmConfigState) -> RegisterState:
        if not isinstance(value, self.config_cls):
            raise TypeError(
                f"Invalid config: expected a {self.config_cls} instance but "
                f"got {value}"
            )
        # "transpose" the bits into the first position of each register
        new_state = [
            self._local_bytes[i].replace(0, BitString(b))
            for i, b in enumerate(str(value.value))
        ]
        return new_state


class Alarm1ConfigParser(AlarmConfigParser[Alarm1ConfigState]):
    config_cls = Alarm1ConfigState


class Alarm2ConfigParser(AlarmConfigParser[Alarm2ConfigState]):
    config_cls = Alarm2ConfigState


class OscillatorEnable(FlagParser):
    """
    Flag EOSC:
     'When set to logic 0, the oscillator is started. When set to
     logic 1, the oscillator is stopped when the DS3231 switches to VBAT. This
     bit is clear (logic 0) when power is first applied. When the DS3231 is
     powered by VCC, the oscillator is always on regardless of the status of
     the EOSC bit. When EOSC is disabled, all register data is static.'
    """


class BatterySquareWaveEnable(FlagParser):
    # TODO: warn that this flag only works if INTCN is 0 (square wave mode)
    """
    Flag BBSQW:
     'When set to logic 1 with INTCN = 0 and VCC < VPF, this bit enables the
     square wave. When BBSQW is logic 0, the INT/SQW pin goes high impedance
     when VCC < VPF.'
    """


class ForceConvertTemperature(FlagParser):
    """
    Flag CONV:
     'Setting this bit to 1 forces the temperature sensor to convert the
     temperature into digital code and execute the TCXO algorithm to update
     the capacitance array to the oscillator. This can only happen when a
     conversion is not already in progress. The user should check the status
     bit BSY before forcing the controller to start a new TCXO execution. A
     user-initiated temperature conversion does not affect the internal 64-
     second update cycle.

     A user-initiated temperature conversion does not affect the BSY bit for
     approximately 2ms. The CONV bit remains at a 1 from the time it is written
     until the conversion is finished, at which time both CONV and BSY go to 0.
     The CONV bit should be used when monitoring the status of a user-initiated
     conversion.'
    """
