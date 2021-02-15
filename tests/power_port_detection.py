# Power Port Detection - By: cwallis

# Use this script to control how your OpenMV Cam captures images for your dataset.
# You should apply the same image pre-processing steps you expect to run on images
# that you will feed to your model during run-time.

# If somebody walks in front of the target it will not shoot
# I am going to pretend it's a safety thing even though it's just because
# it hates me less this way - Celia

import sensor, image, time, math, pyb
import frc_pixie
import frc_can
from pyb import UART

live = True

pixie = frc_pixie.frc_pixie()
can = frc_can.frc_can(2)

# Set the configuration for our OpenMV frcCAN device.
can.set_config(2, 0, 0, 0)
# Set the mode for our OpenMV frcCAN device.
can.set_mode(1)

sensor.reset()
sensor.set_pixformat(sensor.RGB565) # Modify as you like.
sensor.set_framesize(sensor.QVGA) # Modify as you like.
sensor.skip_frames(time = 2500)

sensor.set_auto_gain(False)
sensor.set_auto_whitebal(False)
sensor.set_auto_exposure(True)

original_exposure = sensor.get_exposure_us()
sensor.set_auto_exposure(False, int(.20 * original_exposure))

clock = time.clock()

uart = UART(1, 115200)

color = bytearray(3)
color[0] = 0x00
color[1] = 0xFF
color[2] = 0x00

if live == False:
    img_reader = image.ImageIO("/stream_jan30.bin", "r")

while(True):
    can.update_frame_counter() # Update the frame counter.
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

    thresholds = [(76, 100, -65, -8, -24, 22)]

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

    thresholds = [(31, 61, -8, 11, 0, 28)]
    blobs = []

    for blob in img.find_blobs(thresholds, pixels_threshold=150, area_threshold=150):
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
    targetGreenBlobs = [];
    targetWhiteBlobs = [];
    targetBlob = None

    for g in greenBlobs:
        for w in whiteBlobs:
            if (w.w() * 3) * 1.3 > g.w() and (w.w() * 3) * 0.7 < g.w() and g.x() < w.x() and g.x() + g.w() > w.x() + w.w() and int(w.y()) < int(g.y()) and int(w.y() + w.h()) > g.y():
                targetGreenBlobs.append(g);
                targetWhiteBlobs.append(w);

    targetArea = 0
    index = 0

    for t in targetGreenBlobs:
        if t.w() * t.h() > targetArea:
            targetArea = t.w() * t.h()
            targetBlob = targetWhiteBlobs[index]
        index = index + 1

        targetX.append(w.cx())
        targetY.append(w.cy())

    for x in targetX:
        img.draw_line(x, 0, x, img.height())

    for y in targetY:
        img.draw_line(0, y, img.width(), y)

    pixie.setColor(color)

    if live == False:
        time.sleep(1.5)

    can.send_heartbeat()


    if len(targetX) == 0 or len(targetY) == 0:
        can.send_advanced_track_data(0, 0, 0, 0, 0, 0)
        #pyb.LED(1).off()
        #pyb.LED(3).on()
    else:
        area = int(3.14159 * (targetBlob.w() / 2 * targetBlob.w() / 2))
        can.send_advanced_track_data(targetBlob.cx(), targetBlob.cy(), area, 0, 11, 0)
        #pyb.LED(1).on()
        #pyb.LED(3).off()
            #TODO: the qual = 11 needs to be chaged with an actual quality filter eventually

    if can.get_frame_counter() % 50 == 0:
        can.send_config_data()
        can.send_camera_status(sensor.width(), sensor.height())

    pyb.delay(70)
    print("HB %d" % can.get_frame_counter())
    can.check_mode();
