# Dataset Capture Script - By: cwallis - Wed Jan 13 2021

# Use this script to control how your OpenMV Cam captures images for your dataset.
# You should apply the same image pre-processing steps you expect to run on images
# that you will feed to your model during run-time.

import sensor, image, time, pyb
import frc_pixie
from pyb import UART

import frc_lidar

lidar = frc_lidar.frc_lidar()

record_time = 10000 # 10 seconds in milliseconds

pixie = frc_pixie.frc_pixie()

sensor.reset()
sensor.set_pixformat(sensor.RGB565) # Modify as you like.
sensor.set_framesize(sensor.QVGA) # Modify as you like.
sensor.skip_frames(time = 2000)

sensor.set_auto_gain(False, gain_db_ceiling = -3)
sensor.set_auto_whitebal(False)
sensor.set_auto_exposure(True)

#sensor.set_saturation(1)

original_exposure = sensor.get_exposure_us()
sensor.set_auto_exposure(False, int(0.15 * original_exposure))


clock = time.clock()

uart = UART(1, 115200)

color = bytearray(3)
color[0] = 0x15
color[1] = 0xFF
color[2] = 0x00

img_writer = image.ImageIO("/test_stream.bin", "w")

start = pyb.millis()
while pyb.elapsed_millis(start) < record_time:
    clock.tick()

    img = sensor.snapshot().gamma_corr(gamma = 1.4, contrast = 1.2, brightness = -0.2)

    pixie.setColor(color)
    time.sleep(0.1);

    #lidar_frame = lidar.readLidar()

    ## Send out our results.
    #print("Frame: %s"%lidar_frame); # Print the line we got back for this frame.

    # Delay to control the rate...
    pyb.delay(30); # Wait a while...

