from frico.devices import FakeDevice

from frico_rtc.devices import DS3231


class FakeDS3231(FakeDevice, DS3231):
    pass


def test_ds3231():
    rtc = FakeDS3231()
    assert rtc
