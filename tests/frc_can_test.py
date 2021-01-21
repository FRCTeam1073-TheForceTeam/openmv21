# FRC CAN Library test - By: rtpac - Sat Jan 25 2020

import sensor, image, time, pyb
# Import the frc_CAN library for talking with the RoboRio
import frc_can


# Test Program Main --------------------------------------------------

sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.skip_frames(time = 2500)

# Creatae our frcCAN object for interfacing with RoboRio over CAN
can = frc_can.frc_can(1)

# Set the configuration for our OpenMV frcCAN device.
can.set_config(1, 0, 0, 0)
# Set the mode for our OpenMV frcCAN device.
can.set_mode(1)

while(True):
    can.update_frame_counter() # Update the frame counter.
    img = sensor.snapshot()

    can.send_heartbeat()       # Send the heartbeat message to the RoboRio
    can.send_advanced_track_data(310, 100, 1099, 5, 77, 0)

    # Occasionally send config data and camera status:
    if can.get_frame_counter() % 50 == 0:
        can.send_config_data()
        can.send_camera_status(320, 240)

    pyb.delay(100)
    print("HB %d" % can.get_frame_counter())
    can.check_mode();
