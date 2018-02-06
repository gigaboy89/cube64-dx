#!/usr/bin/env python3
#
# Classes for communicating with debug devices
#
# --Micah Dowty <micah@navi.cx>
#

import serial, struct

class SerialBridge:
    """Thin abstraction for using the serial_bridge device to calculate
       CRCs for packets using real Nintendo hardware. This assumes
       the serial port has already been set up for the right baud rate
       and such (38400 8-N-1)
       """
    def __init__(self, dev="/dev/ttyUSB0"):
        self.fd = serial.Serial(port=dev, baudrate=38400, timeout=1)

    def write(self, data, replyBytes=0):
        """Write the start-of-command identifier, the tramsmit length,
           receive length, then the data. Reads the proper number of reply
           bytes and returns a (edges_detected, reply) tuple
           """
        r = b''
        while len(r) != replyBytes+1:
            self.fd.write(struct.pack("BBB", 0x7E, len(data), replyBytes) + data)
            r = self.fd.read(replyBytes+1)
        return (bytes([r[0]]), r[1:])

    def busWrite(self, packet, address):
        return self.write(struct.pack(">BH", 3, address) + packet, 1)

    def refCRC(self, packet, address=0x8001):
        """Write the given packet to the controller bus at the given (encoded)
           address, returning the 8-bit CRC generated by the controller hardware.
           I've verified that the address has no effect on the returned CRC.
           """
        return int.from_bytes(self.busWrite(packet, address)[1], byteorder='big')

    def genVectors(self, seq):
        """Given a sequence of test packets, returns a dictionary mapping the packets to CRCs"""
        d = {}
        for packet in seq:
            crc = self.refCRC(packet)
            print("{} -> {:02X}".format(" ".join(["{:02X}".format(b) for b in packet]), crc))
            d[tuple(packet)] = crc
        return d

### The End ###
