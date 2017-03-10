from gps import *
import time

print("Creating GPS object ...")
mygps = GPS();

print("Open GPS ...")
mygps.open()
print("GPS open OK")

# mygps.GetPositions()
print("GPS thread running")
mygps.run()

while 1:
	sleep(1)
	print mygps.Position()
