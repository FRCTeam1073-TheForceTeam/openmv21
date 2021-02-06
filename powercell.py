# Find Circles Example
#
# This example shows off how to find circles in the image using the Hough
# Transform. https://en.wikipedia.org/wiki/Circle_Hough_Transform
#
# Note that the find_circles() method will only find circles which are completely
# inside of the image. Circles which go outside of the image/roi are ignored...

import sensor, image, time, pyb
import frc_can

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
sensor.set_auto_exposure(False, int(.30 * original_exposure))

clock = time.clock()

# Histogram baseline for yellow power-cell
hist = [45, 99, -30, 10, 35, 70]

# Power-Cell tracker is device #2
can = frc_can.frc_can(2)

# Set the configuration for our OpenMV frcCAN device.
can.set_config(2, 0, 0, 0)
# Set the mode for our OpenMV frcCAN device.
can.set_mode(1)

while(True):
    can.update_frame_counter() # Update the frame counter.
    img = sensor.snapshot()

    bestCircle = None

    for blob in img.find_blobs([hist], pixels_threshold=500, area_threshold=500, merge=True, ):
        print (blob)
        #img.draw_rectangle(blob.x(), blob.y(), blob.w(), blob.h())
        blob_roi = (blob.x()-5, blob.y()-5, blob.w()+10, blob.h()+10)
        minr = int((blob.w()-5)/2)
        maxr = int((blob.w()+5)/2)

        for circle in img.find_circles(roi = blob_roi, threshold = 2000, x_margin = 10, y_margin = 10,
                                    r_margin = 10, r_min = minr, r_max = maxr, r_step = 2, merge=True):
            #if ((circle.r()*2 - 10) < blob.w() < (circle.r()*2 + 10)):
            img.draw_circle(circle.x(), circle.y(), circle.r(), color = (0, 55, 200))
            #print(circle)

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
        can.send_camera_status(sensor.width(), sensor.height())

    pyb.delay(70)
    print("HB %d" % can.get_frame_counter())
    can.check_mode();


