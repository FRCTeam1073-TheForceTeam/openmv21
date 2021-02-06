# Dataset Capture Script - By: cwallis - Wed Jan 13 2021

# Use this script to control how your OpenMV Cam captures images for your dataset.
# You should apply the same image pre-processing steps you expect to run on images
# that you will feed to your model during run-time.

import sensor, image, time, pyb
import frc_pixie
from pyb import UART

record_time = 10000 # 10 seconds in milliseconds

pixie = frc_pixie.frc_pixie()

sensor.reset()
sensor.set_pixformat(sensor.RGB565) # Modify as you like.
sensor.set_framesize(sensor.QVGA) # Modify as you like.
sensor.skip_frames(time = 2000)

sensor.set_auto_gain(False)
sensor.set_auto_whitebal(False)
sensor.set_auto_exposure(True)

original_exposure = sensor.get_exposure_us()
sensor.set_auto_exposure(False, int(.30 * original_exposure))

clock = time.clock()

uart = UART(1, 115200)

color = bytearray(3)
color[0] = 0x00
color[1] = 0xFF
color[2] = 0x00

img_writer = image.ImageIO("/test_stream.bin", "w")

start = pyb.millis()
while pyb.elapsed_millis(start) < record_time:
    clock.tick()

    img = sensor.snapshot()

    print(clock.fps())
    img_writer.write(img)

    #pixie.setColor(color)
    print("!")
    time.sleep(0.1);

img_writer.close()
print("Done")
