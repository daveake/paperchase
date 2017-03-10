# Parse LoRa from I2C-connected Arduino
# This sends LoRa packets and GGA packets
# Any disabling or filtering of other NMEA is done by the Arduino

import sys
import pigpio
import math
import threading
from time import sleep

def PayloadChecksumOK(Line):
	return True


def ProcessLine(self, Line):
	if Line[0:2] == '$$':
		if PayloadChecksumOK(Line):
			Fields = Line.split(',')
			
			self.PayloadPosition['id'] = Fields[0][2:]
			self.PayloadPosition['count'] = int(Fields[1])
			self.PayloadPosition['time'] = Fields[2]
			self.PayloadPosition['lat'] = float(Fields[3])
			self.PayloadPosition['lon'] = float(Fields[4])
			self.PayloadPosition['alt'] = int(round(float(Fields[5])))
			print self.PayloadPosition
		else:
			print "Bad checksum"
	else:
		print "Unknown message from AVR: " + Line


class LoRa(object):
	"""
	Gets position from UBlox GPS receiver, using s/w i2c to GPIO pins
	Uses UBX commands; disables any incoming NMEA messages
	Puts GPS into flight mode as required
	Provides emulated GPS option
	Provides callbacks on change of state (e.g. lock attained, lock lost)
	"""
	PortOpen = False
	
	def __init__(self):
		 self.PayloadPosition = {'id': '', 'count': 0, 'time': '00:00:00', 'lat': 0.0, 'lon': 0.0, 'alt': 0}
	
	def __lora_thread(self):
		Line = ''

		while True:
			# try:
				Byte = self.pi.i2c_read_byte(self.handle)
				Character = chr(Byte)
				if Byte == 255:
					sleep(0.1)
				elif (Character == '$') and (Line != '$'):
					Line = Character
				elif len(Line) > 90:
					Line = ''
				elif (Line != '') and (Character != '\r'):
					Line = Line + Character
					if Character == '\n':
						ProcessLine(self, Line)
						Line = ''
			# except:
				# pass

	def open(self):
		self.pi = pigpio.pi()
		self.handle = self.pi.i2c_open(1, 8, 0)		
		return True
	
	def Position(self):
		return self.PayloadPosition
			
	def run(self):
		t = threading.Thread(target=self.__lora_thread)
		t.daemon = True
		t.start()
