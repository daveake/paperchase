import sys
import pigpio

pi = pigpio.pi() # Connect to local Pi.

handle = pi.i2c_open(1, 8, 0)
 
while True:
	try:
		c = pi.i2c_read_byte(handle)
		sys.stdout.write(chr(c))
		if c == '\n':
			sys.stdout.flush()
	except:
		pass
	
pi.i2c_close(handle)
pi.stop()

