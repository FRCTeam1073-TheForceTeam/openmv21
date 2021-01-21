# PIXIE Class
#
# Board connects Pixie to UART1
#
# Pixie protocol is
# 115200, 3 Bytes (R,G,B) then at least a 1ms break.
#

import time
from pyb import UART

class frc_pixie:

    def __init__(self):
        self.uart = UART(1, 115200)

    def setColor(self, color2set):
        self.uart.write(color2set);
        print("color...")
