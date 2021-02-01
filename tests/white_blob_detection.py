# Dataset Capture Script - By: cwallis - Wed Jan 13 2021

# Use this script to control how your OpenMV Cam captures images for your dataset.
# You should apply the same image pre-processing steps you expect to run on images
# that you will feed to your model during run-time.

import sensor, image, time, math
import frc_pixie
from pyb import UART

pixie = frc_pixie.frc_pixie()

thresholds = [(86, 100, -6, 9, -5, 12)]

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

blobs = []
circles = []
actualBlobs = []

img_reader = image.ImageReader("/stream25_jan25.bin")

while(True):
    clock.tick()

    img = img_reader.next_frame(copy_to_fb=True, loop=True, pause=True)

    for blob in img.find_blobs(thresholds, pixels_threshold=200, area_threshold=200):
        # These values depend on the blob not being circular - otherwise they will be shaky.
        # These values are stable all the time.
        blobs.append(blob)

    for b in blobs:
        if b.w() + 3 > b.h() and b.w() - 3 < b.h() :
            actualBlobs.append(b)


    for c in actualBlobs:
        if blob.elongation() > 0.5:
            img.draw_edges(blob.min_corners(), color=(255,0,0))
            img.draw_line(blob.major_axis_line(), color=(0,255,0))
            img.draw_line(blob.minor_axis_line(), color=(0,0,255))
        img.draw_rectangle(blob.rect())
        img.draw_cross(blob.cx(), blob.cy())
        # Note - the blob rotation is unique to 0-180 only.
        img.draw_keypoints([(blob.cx(), blob.cy(), int(math.degrees(blob.rotation())))], size=20)

    print(clock.fps())

    pixie.setColor(color)
    print("!")
    time.sleep(0.7);
