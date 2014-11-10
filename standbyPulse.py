#!/usr/bin/python
"""
Set the entire strip to a uniform color specified by its RGB values.
Example:
$ ./setRGB.py 60 32 19
"""

import sys

if len(sys.argv)>3:
    if int(sys.argv[1])<128:
        r = int(sys.argv[1])
    else:
        print 'all numbers must be between 0 and 127'
        sys.exit(1)
    if int(sys.argv[2])<128:
        g = int(sys.argv[2])
    else:
        print 'all numbers must be between 0 and 127'
        sys.exit(1)
    if int(sys.argv[3])<128:
        b = int(sys.argv[3])
    else:
        print 'all numbers must be between 0 and 127'
        sys.exit(1)
else:
    print 'please enter 3 numbers (RGB) from 0-127'
    sys.exit(1)

spidev  = file('/dev/spidev0.0', "wb")

nleds = 240
nzeros = 15


zeros = bytearray(nzeros)

buff = bytearray(nleds*3)

while(True):
    b +=1
    b %= 6
    for i in range(nleds):
        buff[3*i] = 128+g
        buff[3*i+1] = 128+r
        buff[3*i+2] = 128+b

    	spidev.write(buff+zeros)
    	spidev.flush()
