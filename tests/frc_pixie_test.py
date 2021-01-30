# Untitled - By: cwallis - Wed Jan 20 2021

import sensor, image, time, pyb

import frc_pixie

pixie = frc_pixie.frc_pixie()

#sensor.reset()
#sensor.set_pixformat(sensor.RGB565)
#sensor.set_framesize(sensor.QVGA)
#sensor.skip_frames(time = 2000)

clock = time.clock()

color = bytearray(3)
color[0] = 0x00
color[1] = 0x80
color[2] = 0x00

while(True):
    pixie.setColor(color)

    pyb.delay(100)
