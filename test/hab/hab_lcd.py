import os, sys, time, math
from datetime import datetime
from avr import *

from PIL import Image, ImageDraw, ImageFont
from papirus import Papirus

def CalculateDistance(HABLatitude, HABLongitude, CarLatitude, CarLongitude):
	HABLatitude = HABLatitude * math.pi / 180
	HABLongitude = HABLongitude * math.pi / 180
	CarLatitude = CarLatitude * math.pi / 180
	CarLongitude = CarLongitude * math.pi / 180

	return 6371000 * math.acos(math.sin(CarLatitude) * math.sin(HABLatitude) + math.cos(CarLatitude) * math.cos(HABLatitude) * math.cos(HABLongitude-CarLongitude))

def CalculateDirection(HABLatitude, HABLongitude, CarLatitude, CarLongitude):
	HABLatitude = HABLatitude * math.pi / 180
	HABLongitude = HABLongitude * math.pi / 180
	CarLatitude = CarLatitude * math.pi / 180
	CarLongitude = CarLongitude * math.pi / 180

	y = math.sin(HABLongitude - CarLongitude) * math.cos(HABLatitude)
	x = math.cos(CarLatitude) * math.sin(HABLatitude) - math.sin(CarLatitude) * math.cos(HABLatitude) * math.cos(HABLongitude - CarLongitude)

	return math.atan2(y, x) * 180 / math.pi


WHITE = 1
BLACK = 0

avr = AVR()
avr.open()
avr.run()

papirus = Papirus()

payload_font = ImageFont.truetype('/usr/share/fonts/truetype/freefont/FreeSansBold.ttf', 24)
time_font = ImageFont.truetype('/usr/share/fonts/truetype/freefont/FreeSansBold.ttf', 18)

image = Image.new('1', papirus.size, WHITE)

draw = ImageDraw.Draw(image)

circle_diameter = papirus.size[1]
arrow_length = circle_diameter - 4
x0 = papirus.size[0] - circle_diameter
y0 = 0
x1 = papirus.size[0] - 1
y1 = papirus.size[1] - 1
draw.ellipse([x0, y0, x1, y1], 1, 0)

papirus.display(image)
papirus.update()

OldGPSTime = '00:00:00'
OldHABTime = '00:00:00'
LastPositionAt = None

while True:
	time.sleep(0.5)
	
	HABPosition = avr.HABPosition()
	GPSPosition = avr.GPSPosition()
	
	if HABPosition:
	
		#------------ Payload -------------
		
		draw.rectangle(((0,0),(x0,23)), fill="white", outline = "white")
		draw.text((0,0), HABPosition['id'], font=payload_font, fill=BLACK)

		#------------ Time since payload position ------------
		
		if HABPosition['time'] != OldHABTime:
			LastPositionAt = datetime.utcnow()
		
		if LastPositionAt:
			draw.rectangle(((0,72),(x0,95)), fill="white", outline = "white")
			draw.text((0,72), str(int((datetime.utcnow() - LastPositionAt).total_seconds())) + ' s', font=time_font, fill=BLACK)
		
		if GPSPosition['sats'] > 0:
		
			#----------- distance and direction -----------
			DistanceToHAB = CalculateDistance(HABPosition['lat'], HABPosition['lon'], GPSPosition['lat'], GPSPosition['lon'])
			DirectionToHAB = CalculateDirection(HABPosition['lat'], HABPosition['lon'], GPSPosition['lat'], GPSPosition['lon'])
			DirectionToHAB = (int(DirectionToHAB) + 270) % 260
		
			#----------- arrow -----------
			
			# clear centre of circle
			draw.ellipse([x0+2, y0+2, x1-2, y1-2], 1, 1)

			# draw direction
			draw.pieslice([x0+2, y0+2, x1-2, y1-2], DirectionToHAB-10, DirectionToHAB+10, 0, 0)
	
	
			#------------ Distance ------------
			
			draw.rectangle(((0,36),(x0-1,59)), fill="white", outline = "white")
			draw.text((0,36), str(int(DistanceToHAB)) + 'm', font=payload_font, fill=BLACK)

	
	#------------ Update display ----------
	
	papirus.display(image)
		
	if GPSPosition['time'][6:8] == '30':
		papirus.update()
	else:
		papirus.partial_update()	

	OldHABTime = HABPosition['time']
	OldGPSTime = GPSPosition['time']

		