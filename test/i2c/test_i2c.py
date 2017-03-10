import pigpio

pi = pigpio.pi() # connect to local Pi

for device in range(128):
	h = pi.i2c_open(1, device)
	try:
		pi.i2c_read_byte(h)
		print(hex(device))
	except: # exception if i2c_read_byte fails
		pass
	pi.i2c_close(h)

pi.stop # disconnect from Pi

