# Untitled - By: cwallis - Sat Jan 23 2021

import sensor, image, time

import time
from pyb import UART
import pyb


class frc_lidar:
    def __init__(self):
        # Always pass UART 3 for the UART number for your OpenMV Cam.
        self.uart = UART(3);

        # This initializes the UART paramters: 115200 bits/second, 8 bits/byte, no parity, 1 stop.
        # Wait for 80ms for data to start when reading and up to 20ms between characters before
        # we timeout on reading.
        self.uart.init(115200, bits=8, parity=None, stop=1, timeout_char=20, timeout=80);

        # First we have to stop it from talking so we can send commands
        # and understand what it says back.
        # Disable output command:
        self.command = bytes(b'\x5A\x05\x07\x00\x66');
        self.uart.write(self.command);
        self.uart.read();

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
        self.response = self.uart.read();


        # Now Read Version Info: Now we know that the next response will be to this command.
        self.command = bytes(b'\x5A\x04\x01\x5F');
        self.uart.write(self.command);
        self.uart.read();
        #print("Version Command: %s"%command);
        #uart.write(command);
        # Read back response:
        #response = uart.read();
        #print("Version Response[%d]: %s"%(len(response), response));

        # Set the format of data to be text (easily parsed):
        # We could send another command to set the binary format and then
        # we would receive packets of 9 bytes for each reading.
        self.command = bytes(b'\x5A\x05\x05\x02\x66');
        self.uart.write(self.command);
        self.uart.read();
        #print("Format Command: %s"%command);
        #uart.write(command);
        # Read back response:
        #response = uart.read();
        #print("Format Response[%d]: %s"%(len(response),response));

        # Set the rate to zero so we trigger it to capture and can sync with
        # other things we do in the OpenMV. It will respond when we ask so
        # we can't get out of sync with it.
        self.command = bytes(b'\x5A\x06\x03\x00\x00\x63');
        self.uart.write(self.command);
        self.uart.read();
        # print("Rate Command: %s"%command);
        # uart.write(command);
        # response = uart.read();
        # print("Rate Response[%d]: %s"%(len(response),response));

        # Enable output again now that we're ready:
        self.command = bytes(b'\x5A\x05\x07\x01\x67');
        self.uart.write(self.command);
        self.uart.read();
        # print("Enable Command: %s"%command);
        # uart.write(command);
        # response = uart.read(5);
        # print("Enable Response[%d]: %s"%(len(response),response));

    def readLidar(self):
        self.command = bytes(b'\x5A\x04\x04\x62'); # Trigger detection command
        self.uart.write(self.command); # Send the trigger over the UART
        # If we were going to do image processing at the same time we would do it
        # here while the UART is receiving characters in the background... that way
        # we can get the data from the TF-LIDAR while we're running our image processing
        # and then use it once we're done and the loop runs as fast as possible.

        # Do Image processing stuff...

        # Read the lidar since it has had time for characters to come over the serial port.
        self.lidar_frame = self.uart.readline(); # Read until the newline character (we picked text format with newline above)


        return self.lidar_frame
