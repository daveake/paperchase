# Parse GPS from I2C-connected Arduino
# This sends LoRa packets and GGA packets
# Any disabling or filtering of other NMEA is done by the Arduino

import sys
import pigpio
import math
import threading
from time import sleep

def GPSChecksumOK(Line):
	Count = len(Line)

	XOR = 0;

	for i in range(1, Count-4):
		c = ord(Line[i])
		XOR ^= c

	return (Line[Count-4] == '*') and (Line[Count-3:Count-1] == hex(XOR)[2:4].upper())

	
def FixPosition(Position):
	Position = Position / 100

	MinutesSeconds = math.modf(Position)

	return MinutesSeconds[1] + MinutesSeconds[0] * 5 / 3


def ProcessLine(self, Line):
	if Line[0:2] == '$$':
		pass
		# print "Payload packet"
	elif Line[0] == '$':
		if GPSChecksumOK(Line):
			if Line[3:6] == "GGA":
				# $GNGGA,213511.00,5157.01416,N,00232.65975,W,1,12,0.64,149.8,M,48.6,M,,*55
				Fields = Line.split(',')
				
				if Fields[1] != '':
					self.GPSPosition['time'] = Fields[1][0:2] + ':' + Fields[1][2:4] + ':' + Fields[1][4:6]
					if Fields[2] != '':
						self.GPSPosition['lat'] = FixPosition(float(Fields[2]))
						if Fields[3] == 'S':
							self.GPSPosition['lat'] = -self.GPSPosition['lat']
						self.GPSPosition['lon'] = FixPosition(float(Fields[4]))
						if Fields[5] == 'W':
							self.GPSPosition['lon'] = -self.GPSPosition['lon']
						self.GPSPosition['alt'] = float(Fields[9])
				if self.GPSPosition['fix'] != int(Fields[6]):
					self.GPSPosition['fix'] = int(Fields[6])
					if self.GPSPosition['fix'] > 0:
						if self._WhenLockGained != None:
							self._WhenLockGained()
					else:
						print("FIX TYPE = ", GPSPosition['fix'])
						if self._WhenLockLost != None:
							self._WhenLockLost()
				self.GPSPosition['sats'] = int(Fields[7])
				print self.GPSPosition
			else:
				print "Unknown NMEA sentence from AVR: " + Line
		else:
			print "Bad checksum"
	else:
		print "Unknown message from AVR: " + Line


class GPS(object):
	"""
	Gets position from UBlox GPS receiver, using s/w i2c to GPIO pins
	Uses UBX commands; disables any incoming NMEA messages
	Puts GPS into flight mode as required
	Provides emulated GPS option
	Provides callbacks on change of state (e.g. lock attained, lock lost)
	"""
	PortOpen = False
	
	def __init__(self):
		 self._WhenLockGained = None
		 self._WhenLockLost = None
		 self.GPSPosition = {'time': '00:00:00', 'lat': 0.0, 'lon': 0.0, 'alt': 0, 'sats': 0, 'fix': 0}
	
	def __gps_thread(self):
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
		return self.GPSPosition
			
	@property
	def WhenLockGained(self):
		return self._WhenLockGained

	@WhenLockGained.setter
	def WhenLockGained(self, value):
		self._WhenLockGained = value
	
	@property
	def WhenLockLost(self):
		return self._WhenLockLost

	@WhenLockLost.setter
	def WhenLockGained(self, value):
		self._WhenLockLost = value
	
	def run(self):
		t = threading.Thread(target=self.__gps_thread)
		t.daemon = True
		t.start()
