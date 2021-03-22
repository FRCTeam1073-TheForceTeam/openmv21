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

pixie = frc_pixie.frc_pixie()
can = frc_can.frc_can(1)

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
sensor.set_auto_exposure(False, int(.10 * original_exposure))

clock = time.clock()

uart = UART(1, 115200)

color = bytearray(3)
color[0] = 0x00
color[1] = 0xFF
color[2] = 0x00

roi = (0, 0, 332, 190)

thresholdsG = [(61, 100, -76, -9, -24, 46)]

#lidar initialization
uart = UART(3)
uart.init(115200, bits=8, parity=None, stop=1, timeout_char=20, timeout=80);

#lidar setup
def lidar_command(command, purpose):
    if purpose:
        print("%s Command : %s"%(purpose, command))
    uart.write(command);
    response = uart.read();
    if purpose:
        print("%s Response : %s"%(purpose, response))
    return purpose

command = bytes(b'\x5A\x05\x07\x00\x66');
lidar_command(command, "Disable");

#read lidar
response = uart.read();

command = bytes(b'\x5A\x04\x01\x5F');
lidar_command(command, "Version");
command = bytes(b'\x5A\x05\x05\x02\x66');
lidar_command(command, "Format");
command = bytes(b'\x5A\x06\x03\x00\x00\x63');
lidar_command(command, "Rate");
command = bytes(b'\x5A\x05\x07\x01\x67');
lidar_command(command, "Enable");

while(True):
    can.update_frame_counter() # Update the frame counter.
    clock.tick()

    img = sensor.snapshot()

    #lidar
    command = bytes(b'\x5A\x04\x04\x62');
    uart.write(command);

    greenBlobs = img.find_blobs(thresholdsG, pixels_threshold=50, area_threshold=200, roi=roi)

    #for blob in img.find_blobs(thresholdsG, pixels_threshold=200, area_threshold=200, roi=roi):
        ## These values depend on the blob not being circular - otherwise they will be shaky.
        ## These values are stable all the time.
        #greenBlobs.append(blob)

        #if blob.elongation() > 0.5:
            #img.draw_edges(blob.min_corners(), color=(255,0,0))
            #img.draw_line(blob.major_axis_line(), color=(0,255,0))
            #img.draw_line(blob.minor_axis_line(), color=(0,0,255))
        #img.draw_rectangle(blob.rect())
        #img.draw_cross(blob.cx(), blob.cy())
        ## Note - the blob rotation is unique to 0-180 only.
        #img.draw_keypoints([(blob.cx(), blob.cy(), int(math.degrees(blob.rotation())))], size=20)

    targetBlob = None
    #targetX = []
    #targetY = []

    targetArea = 0

    for t in greenBlobs:
        if t.w() * t.h() > targetArea:
            targetArea = t.w() * t.h()
            targetBlob = t

        #img.draw_line(t.cx(), 0, t.cx(), img.height())
        #img.draw_line(0, t.y(), img.width(), t.y())

    #whiteBlobs = img.find_blobs(thresholdsW, pixels_threshold=200, area_threshold=200, roi=(targetBlob.x(), targetBlob.y(), targetBlob.w(), targetBlob.h()))

    innerTarget = None

    #innerTargetArea = 0

    #for t in whiteBlobs:
        #if t.w() * t.h() > innerTargetArea:
            #innerTargetArea = t.w() * t.h()
            #innerTarget = t

    can.send_heartbeat()


    if targetBlob == None:
        can.send_advanced_track_data(0, 0, 0, 0, 0, 0)
        pyb.LED(1).off()
        pyb.LED(3).on()
    else:
        area = int(3.14159 * (targetBlob.w() / 2 * targetBlob.w() / 2))
        if innerTarget != None:
            x = (targetBlob.cx() + innerTarget.cx()) / 2
            y = innerTarget.cy()
        else:
            x = targetBlob.cx()
            y = targetBlob.y()

        can.send_advanced_track_data(x, y, area, 0, 11, 0)
        pyb.LED(1).on()
        pyb.LED(3).off()

        img.draw_edges(targetBlob.min_corners(), color=(255,0,0))
        img.draw_line(targetBlob.major_axis_line(), color=(0,255,0))
        img.draw_line(targetBlob.minor_axis_line(), color=(0,0,255))
        img.draw_rectangle(targetBlob.rect(), color=(255, 0, 0))
        img.draw_cross(targetBlob.cx(), targetBlob.cy())
        # Note - the blob rotation is unique to 0-180 only.
        #TODO: the qual = 11 needs to be chaged with an actual quality filter eventually

    if can.get_frame_counter() % 50 == 0:
        can.send_config_data()
        can.send_camera_status(sensor.width(), sensor.height())

    #PARSE THE RANGE DATA AND THEN SEE IT
    lidar_frame = uart.readline()
    if lidar_frame != None:
        #print("Frame: %s"%lidar_frame);
        lidar_range = float(lidar_frame)
        #print("Range: %f"%lidar_range)
        can.send_range_data(int(lidar_range * 1000), 11)
    else:
        can.send_range_data(0, 0)

    pyb.delay(30)

    pixie.setColor(color)

    #print("HB %d" % can.get_frame_counter())
    #can.check_mode();
