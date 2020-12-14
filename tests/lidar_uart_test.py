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

# Always pass UART 3 for the UART number for your OpenMV Cam.
uart = UART(3);

# This initializes the UART paramters: 115200 bits/second, 8 bits/byte, no parity, 1 stop.
# Wait for 80ms for data to start when reading and up to 20ms between characters before
# we timeout on reading.
uart.init(115200, bits=8, parity=None, stop=1, timeout_char=20, timeout=80);


# Define a function for sending a command and reading back response
# to use over and over:
def lidar_command(command, purpose):
    if purpose:
        print("%s Command : %s"%(purpose, command)
    uart.write(command);
    response = uart.read();
    if purpose:
        print("%s Response : %s"%(purpose, response)
    return purpose


# First we have to stop it from talking so we can send commands
# and understand what it says back.
# Disable output command:
command = bytes(b'\x5A\x05\x07\x00\x66');
lidar_command(command, "Disable");

#print("Disable Command: %s"%command);
#uart.write(command);
#response = uart.read();
#print("Disable Response[%d]: %s"%(len(response),response));

# Manal synchronizing with device
#
# Wait  1/4 second for it to shut up, so we can get synchronized with what it is
# sending to us.
pyb.delay(250);   # Delay is in milliseconds.

# Read everything we've got in the UART buffer so far and ignore it...because
# it is just a jumble of stuff we don't know where the frames begin or end.
response = uart.read();


# Now Read Version Info: Now we know that the next response will be to this command.
command = bytes(b'\x5A\x04\x01\x5F');
lidar_command(command, "Version");
#print("Version Command: %s"%command);
#uart.write(command);
# Read back response:
#response = uart.read();
#print("Version Response[%d]: %s"%(len(response), response));

# Set the format of data to be text (easily parsed):
# We could send another command to set the binary format and then
# we would receive packets of 9 bytes for each reading.
command = bytes(b'\x5A\x05\x05\x02\x66');
lidar_command(command, "Format");
#print("Format Command: %s"%command);
#uart.write(command);
# Read back response:
#response = uart.read();
#print("Format Response[%d]: %s"%(len(response),response));

# Set the rate to zero so we trigger it to capture and can sync with
# other things we do in the OpenMV. It will respond when we ask so
# we can't get out of sync with it.
command = bytes(b'\x5A\x06\x03\x00\x00\x63');
lidar_command(command, "Rate");
# print("Rate Command: %s"%command);
# uart.write(command);
# response = uart.read();
# print("Rate Response[%d]: %s"%(len(response),response));

# Enable output again now that we're ready:
command = bytes(b'\x5A\x05\x07\x01\x67');
lidar_command(command, "Enable");
# print("Enable Command: %s"%command);
# uart.write(command);
# response = uart.read(5);
# print("Enable Response[%d]: %s"%(len(response),response));


# Test loop of sending trigger and reading the line (ends in newline)
# for that response. If we picked the binary format packet with our
# format command we would not use readline() we would read the
# specified number of bytes in the binary protocol like frame = uart.read(9);
# and then parse that based on the manual.
while(True):
    command = bytes(b'\x5A\x04\x04\x62'); # Trigger detection command
    uart.write(command); # Send the trigger over the UART
    # If we were going to do image processing at the same time we would do it
    # here while the UART is receiving characters in the background... that way
    # we can get the data from the TF-LIDAR while we're running our image processing
    # and then use it once we're done and the loop runs as fast as possible.

    # Do Image processing stuff...

    # Read the lidar since it has had time for characters to come over the serial port.
    lidar_frame = uart.readline(); # Read until the newline character (we picked text format with newline above)

    # Send out our results.
    print("Frame: %s"%lidar_frame); # Print the line we got back for this frame.

    # Delay to control the rate...
    pyb.delay(30); # Wait a while...



