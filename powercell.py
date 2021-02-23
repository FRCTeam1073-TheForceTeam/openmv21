# Find Circles Example
#
# This example shows off how to find circles in the image using the Hough
# Transform. https://en.wikipedia.org/wiki/Circle_Hough_Transform
#
# Note that the find_circles() method will only find circles which are completely
# inside of the image. Circles which go outside of the image/roi are ignored...

import sensor, image, time, pyb
import frc_can
from pyb import UART

sensor.reset()
sensor.set_pixformat(sensor.RGB565) # grayscale is faster
sensor.set_framesize(sensor.QVGA)
sensor.skip_frames(time = 2500)
sensor.set_auto_exposure(False)
sensor.set_auto_gain(False)
sensor.set_auto_whitebal(False)

pyb.LED(1).off()
pyb.LED(3).off()

original_exposure = sensor.get_exposure_us()
sensor.set_auto_exposure(False, int(.40 * original_exposure))

clock = time.clock()
hist = [15, 95, -15, 20, 25, 80]
testHist = [15, 99, -25, 20, 15, 65]

can = frc_can.frc_can(2)

# Set the configuration for our OpenMV frcCAN device.
can.set_config(2, 0, 0, 0)
# Set the mode for our OpenMV frcCAN device.
can.set_mode(1)

pc_roi = (0, 110, 325, 120)
mag_roi = (0, 155, 320, 90)


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
    #img = sensor.snapshot()
    img = sensor.snapshot().lens_corr(strength=1.8)

    bestCircle = None

    #lidar
    command = bytes(b'\x5A\x04\x04\x62');
    uart.write(command);

    #pc tracking
    for blob in img.find_blobs([hist], roi = pc_roi, pixels_threshold=75, area_threshold=75, merge=True, ):
        print (blob)
        #img.draw_rectangle(blob.x(), blob.y(), blob.w(), blob.h())
        blob_roi = (blob.x()-5, blob.y()-5, blob.w()+10, blob.h()+10)
        minr = int((blob.w()-5)/2)
        maxr = int((blob.w()+5)/2)

        for circle in img.find_circles(roi = blob_roi, threshold = 2000, x_margin = 10, y_margin = 10,
                                    r_margin = 10, r_min = minr, r_max = maxr, r_step = 2, merge=True):
            #if ((circle.r()*2 - 10) < blob.w() < (circle.r()*2 + 10)):
            img.draw_circle(circle.x(), circle.y(), circle.r(), color = (0, 55, 200))
            print(circle)

            #filtering for the closest powercell to the collector, compares and keeps closest PC
            if bestCircle == None:
                bestCircle = circle
            elif bestCircle.y() < circle.y():
                bestCircle = circle

    can.send_heartbeat()       # Send the heartbeat message to the RoboRio

    if bestCircle == None:
        can.send_advanced_track_data(0, 0, 0, 0, 0, 0)
        pyb.LED(1).off()
        pyb.LED(3).on()
    else:
        area = int(3.14159 * (bestCircle.r() * bestCircle.r()))
        can.send_advanced_track_data(bestCircle.x(), bestCircle.y(), area, 0, 11, 0)
        img.draw_circle(bestCircle.x(), bestCircle.y(), bestCircle.r(), color = (255, 0, 0))
        pyb.LED(1).on()
        pyb.LED(3).off()
                #TODO: the qual = 11 needs to be chaged with an actual quality filter eventually

    if can.get_frame_counter() % 50 == 0:
        can.send_config_data()
        can.send_camera_status(320, 240)

    #PARSE THE RANGE DATA AND THEN SEE IT
    lidar_frame = uart.readline();
    print("Frame: %s"%lidar_frame);
    can.send_range_data(2, 3)

    pyb.delay(10)
    print("HB %d" % can.get_frame_counter())
    can.check_mode();


