import utime

class DS3231:
    def __init__(self, i2c, addr=0x68):
        self.i2c = i2c
        self.addr = addr

    def _bcd2dec(self, b):
        return (b >> 4) * 10 + (b & 0x0F)

    def _dec2bcd(self, val):
        return (val // 10) << 4 | (val % 10)

    def get_time(self):
        data = self.i2c.readfrom_mem(self.addr, 0x00, 7)
        sec = self._bcd2dec(data[0])
        minute = self._bcd2dec(data[1])
        hour = self._bcd2dec(data[2])
        weekday = self._bcd2dec(data[3])
        day = self._bcd2dec(data[4])
        month = self._bcd2dec(data[5] & 0x1F)
        year = self._bcd2dec(data[6]) + 2000
        return (year, month, day, hour, minute, sec, weekday, 0)

    def set_time(self, dt):
        # dt is tuple: (year, month, day, hour, minute, second, weekday)
        self.i2c.writeto_mem(self.addr, 0x00, bytes([
            self._dec2bcd(dt[5]),
            self._dec2bcd(dt[4]),
            self._dec2bcd(dt[3]),
            self._dec2bcd(dt[6]),
            self._dec2bcd(dt[2]),
            self._dec2bcd(dt[1]),
            self._dec2bcd(dt[0] - 2000)
        ]))
