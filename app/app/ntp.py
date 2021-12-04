try:
    import usocket as socket
except:
    import socket
try:
    import ustruct as struct
except:
    import struct
import time

# (date(2000, 1, 1) - date(1900, 1, 1)).days * 24*60*60
NTP_DELTA = 3155673600

# The NTP host can be configured at runtime by doing: ntptime.host = 'myhost.org'
host = "pool.ntp.org"


def T_time():
    NTP_QUERY = bytearray(48)
    NTP_QUERY[0] = 0x1B
    addr = socket.getaddrinfo(host, 123)[0][-1]
    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.settimeout(5)
            res = s.sendto(NTP_QUERY, addr)
            msg = s.recv(48)
        except:
            try:
                s.close()
            except:
                pass
            pass
        finally:
            try:
                s.close()
            except:
                pass
            break
    val = struct.unpack("!I", msg[40:44])[0]
    return val - NTP_DELTA


# There's currently no timezone support in MicroPython, so
# utime.localtime() will return UTC time (as if it was .gmtime())
def settime():
    i = 0
    while i < 10:
        try:
            t = T_time()
            break
        except:
            i += 1
            time.sleep(3)
            continue
    import machine
    if i == 10:
        machine.reset()
    import utime
    tm = utime.localtime(t)
    machine.RTC().datetime((tm[0], tm[1], tm[2], tm[6] + 1, tm[3], tm[4], tm[5], 0))
