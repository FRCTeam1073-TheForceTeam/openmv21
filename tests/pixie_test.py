# PIXIE TEST
#
# Board connects Pixie to UART1
#
# Pixie protocol is
# 115200, 3 Bytes (R,G,B) then at least a 1ms break.
#

import time
from pyb import UART

uart = UART(1, 115200)

color = bytearray(3)
color[0] = 0x00
color[1] = 0x80
color[2] = 0x00

while True:
    uart.write(color);
    print("!")
    color[2] = color[2] + 1
    time.sleep(0.5);
