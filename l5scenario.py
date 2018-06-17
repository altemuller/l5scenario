#!/usr/bin/python3

'''
Langrisser V SCEN Tool
A tool to extract and rebuild SCEN files in Langrisser V PSX.
Version:   1.0
Author:    Derrick Sobodash <derrick@sobodash.com>
Copyright: (c) 2008, 2012 Derrick Sobodash
2018 Dmitry Mikhaltsov (Python 3 migration)
Web site:  https://github.com/sobodash/l5scenario/
License:   BSD License <http://opensource.org/licenses/bsd-license.php>
'''

# Simple function to add leading zeros
def addzeros(n):
    n = str(n)
    while(len(n) < 3):
        n = "0" + n
    return n

# Initialize the program

try:
    import sys
    import glob
    import os
    import re
    from struct import *
    import time
    from stat import *
except ImportError as err:
    print ("Could not load %s module." % err)
    raise SystemExit

print("Langrisser V SCEN Tool (cli)\nCopyright (c) 2008, 2012 Derrick Sobodash\n2018 Dmitry Mikhaltsov (Python 3 migration)")

# Test the input and see if we got a file

if len(sys.argv) < 2:
    print ("No input file or directory specified! Try using --help")
    raise SystemExit

elif sys.argv[1] == "--help":
    print ("Extract usage:")
    print ("l5scen.py [FILENAME]")
    print ("Insert Usage:")
    print ("l5scen.py [DIR] [FILENAME]")
    raise SystemExit

if len(sys.argv) == 2:
    file = sys.argv[1]

    # Open the file for processing

    f = open(file, "rb")
    size = os.stat(file)[ST_SIZE]
    offset = 0
    points = []

    # Read all the pointers in and end when we hit a pointer equal to filesize

    while offset != size:
        offset = unpack("<L", f.read(4))
        offset = offset[0]
        points.append(offset)
    print ("Found " + str(len(points) - 1) + " pointers...")

    # Seek to each pointer and write out the content from it to the next pointer
    # to a unique file

    if os.path.exists("l5chunks") == False:
        os.mkdir("l5chunks")

    for i in range(0, len(points) - 1):
        o = open(os.path.join("l5chunks", "sc" + addzeros(i) + ".bin"), "wb")
        f.seek(points[i])
        o.write(f.read(points[i+1] - points[i]))
        print ("Reading chunk " + str(i) + " (" + str(points[i+1] - points[i]) + " bytes)...")
    f.close()

    print ("Complete.")

elif len(sys.argv) == 3:
    dir = sys.argv[1]
    file = sys.argv[2]

    # Check all the files and make sure they are a multiple of 0x800 bytes.
    # If not, pad them.

    print ("Padding files to fill CD sectors...")
    dirlist = glob.glob(os.path.join(dir, "*.bin"))
    dirlist.sort()
    dirsize = []
    for scfile in dirlist:
        size = os.stat(scfile)[ST_SIZE]
        if size % 0x800 != 0:
            f = open(scfile, "rb+")
            f.seek(size)
            while os.stat(scfile)[ST_SIZE] % 0x800 != 0:
                f.write(b'\x00')
                f.flush()
            f.close()
        # Store the padded size
        dirsize.append(size)
	
    # Create a new file and write all the sizes to the header,
    # then pad to 0x800

    print ("Generating " + file + "...")
    o = open(file, "wb")
    offset = 0x800
    o.write(pack("<L", offset))
    o.close()
    
    o = open(file, "rb+")
    
    for i in range(0, len(dirsize)):
        offset += dirsize[i]
        o.write(pack("<L", offset))
    while os.stat(file)[ST_SIZE] % 0x800 != 0:
        o.write(b'\x00')
        o.flush()

    # Now open each file and write its content onto the end

    for scfile in dirlist:
        f = open(scfile, "rb")
        size = os.stat(scfile)[ST_SIZE]
        o.write(f.read(size))
        f.close()

    print ("Complete.")

else:
    print ("DIVISION BY 0 OH SH--")
