# UART Control
#
# This example shows how to use the serial port on your OpenMV Cam to
# talk to a TF-MINI Plus LIDAR and get synchronized to its output data.
#
# First you need to stop it talking in order to get synchronized
# with the data stream.
# Then you select the format.
# Then you select the rate (manually triggered in this case)
# Then you turn the output back on.
# Then you can send a trigger and read a response for range
#   whenever you want.
#

import time
from pyb import UART
import pyb
import frc_lidar

lidar = frc_lidar.frc_lidar()

# Test loop of sending trigger and reading the line (ends in newline)
# for that response. If we picked the binary format packet with our
# format command we would not use readline() we would read the
# specified number of bytes in the binary protocol like frame = uart.read(9);
# and then parse that based on the manual.
while(True):
    lidar_frame = lidar.readLidar()

    # Send out our results.
    print("Frame: %s"%lidar_frame); # Print the line we got back for this frame.

    # Delay to control the rate...
    pyb.delay(30); # Wait a while...
