#! /usr/bin/env python2.7
import sys
f = open(sys.argv[1], 'r')

f.seek(1,2)
f.read(1) # read last byte
sz = f.tell() # get file size

# read up to quarter of the file
# in increasingly larger chunks
def read_exp():
    start= f.tell()
    counter = 12 # (read 1 4KB block or more)

    # keep reading until covered 1/4 of the file
    while  (f.tell() - start) < sz/4:
        f.read(2**counter)
        # read sizes of up to 2**30 = 1GB
        if counter < 30:
            counter+=1

f.seek(0) 
read_exp()

f.seek(sz/2)
read_exp()

f.seek(sz/4)
read_exp()

f.seek((sz/4)*3)
read_exp()
