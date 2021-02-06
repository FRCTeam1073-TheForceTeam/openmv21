# Power Port Detection - By: cwallis

# Use this script to control how your OpenMV Cam captures images for your dataset.
# You should apply the same image pre-processing steps you expect to run on images
# that you will feed to your model during run-time.

# If somebody walks in front of the target it will not shoot
# I am going to pretend it's a safety thing even though it's just because
# it hates me less this way - Celia

import sensor, image, time, math
import frc_pixie
from pyb import UART

live = True

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

if live == False:
    img_reader = image.ImageReader("/stream_jan30.bin")

while(True):
    clock.tick()

    blobs = []
    greenBlobs = []
    whiteBlobs = []
    targetX = []
    targetY = []
    if live == False:
        img = img_reader.next_frame(copy_to_fb=True, loop=True, pause=True)
    else:
        img = sensor.snapshot()

    thresholds = [(98, 100, -7, 8, -8, 0)]

    for blob in img.find_blobs(thresholds, pixels_threshold=200, area_threshold=200):
        # These values depend on the blob not being circular - otherwise they will be shaky.
        # These values are stable all the time.
        greenBlobs.append(blob)

    #for c in greenBlobs:
        #if blob.elongation() > 0.5:
            #img.draw_edges(blob.min_corners(), color=(255,0,0))
            #img.draw_line(blob.major_axis_line(), color=(0,255,0))
            #img.draw_line(blob.minor_axis_line(), color=(0,0,255))
        #img.draw_rectangle(blob.rect())
        #img.draw_cross(blob.cx(), blob.cy())
        ## Note - the blob rotation is unique to 0-180 only.
        #img.draw_keypoints([(blob.cx(), blob.cy(), int(math.degrees(blob.rotation())))], size=20)

    thresholds = [(76, 100, -16, -1, 4, 28)]
    blobs = []

    for blob in img.find_blobs(thresholds, pixels_threshold=200, area_threshold=200):
        # These values depend on the blob not being circular - otherwise they will be shaky.
        # These values are stable all the time.
        whiteBlobs.append(blob)

    #for c in whiteBlobs:
        #if blob.elongation() > 0.5:
            #img.draw_edges(blob.min_corners(), color=(255,0,0))
            #img.draw_line(blob.major_axis_line(), color=(0,255,0))
            #img.draw_line(blob.minor_axis_line(), color=(0,0,255))
        #img.draw_rectangle(blob.rect(), color=(255, 0, 0))
        #img.draw_cross(blob.cx(), blob.cy())
        ## Note - the blob rotation is unique to 0-180 only.
        #img.draw_keypoints([(blob.cx(), blob.cy(), int(math.degrees(blob.rotation())))], size=20)

    for g in greenBlobs:
        for w in whiteBlobs:
            if (w.w() * 3) * 1.2 > g.w() and (w.w() * 3) * 0.8 < g.w() and int(g.cx()) > int(w.cx() - 5) and int(g.cx()) < int(w.cx() + 5) and int(w.y()) < int(g.y()) and int(w.y() + w.h()) > g.y():
                targetX.append(w.cx())
                targetY.append(w.cy())

    for x in targetX:
        img.draw_line(x, 0, x, img.height())

    for y in targetY:
        img.draw_line(0, y, img.width(), y)

    pixie.setColor(color)
    print("!")
    if live == False:
        time.sleep(0.7)
