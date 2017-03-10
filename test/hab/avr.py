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


class AVR(object):
	def __init__(self):
		 self.__GPSPosition = {'time': '00:00:00', 'lat': 0.0, 'lon': 0.0, 'alt': 0, 'sats': 0}
		 self.__HABPosition = {'id': '', 'count': 0, 'time': '00:00:00', 'lat': 0.0, 'lon': 0.0, 'alt': 0}
	
	def __ProcessLine(self, Line):
		if Line[0:2] == '$$':
			if PayloadChecksumOK(Line):
				Fields = Line.split(',')
				
				self.__HABPosition['id'] = Fields[0][2:]
				self.__HABPosition['count'] = int(Fields[1])
				self.__HABPosition['time'] = Fields[2]
				self.__HABPosition['lat'] = float(Fields[3])
				self.__HABPosition['lon'] = float(Fields[4])
				self.__HABPosition['alt'] = int(round(float(Fields[5])))
				print self.__HABPosition
			else:
				print "Bad checksum"
		elif Line[0] == '$':
			if GPSChecksumOK(Line):
				if Line[3:6] == "GGA":
					# $GNGGA,213511.00,5157.01416,N,00232.65975,W,1,12,0.64,149.8,M,48.6,M,,*55
					Fields = Line.split(',')
					
					if Fields[1] != '':
						self.__GPSPosition['time'] = Fields[1][0:2] + ':' + Fields[1][2:4] + ':' + Fields[1][4:6]
						if Fields[2] != '':
							self.__GPSPosition['lat'] = FixPosition(float(Fields[2]))
							if Fields[3] == 'S':
								self.__GPSPosition['lat'] = -self.__GPSPosition['lat']
							self.__GPSPosition['lon'] = FixPosition(float(Fields[4]))
							if Fields[5] == 'W':
								self.__GPSPosition['lon'] = -self.__GPSPosition['lon']
							self.__GPSPosition['alt'] = float(Fields[9])
					self.__GPSPosition['sats'] = int(Fields[7])
					print self.__GPSPosition
				else:
					print "Unknown NMEA sentence from AVR: " + Line
			else:
				print "Bad checksum"
		else:
			print "Unknown message from AVR: " + Line
			
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
						self.__ProcessLine(Line)
						Line = ''
			# except:
				# pass

	def open(self):
		self.pi = pigpio.pi()
		self.handle = self.pi.i2c_open(1, 8, 0)		
		return True
	
	def HABPosition(self):
		return self.__HABPosition
			
	def GPSPosition(self):
		return self.__GPSPosition
			
	def run(self):
		t = threading.Thread(target=self.__lora_thread)
		t.daemon = True
		t.start()
