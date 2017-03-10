import os
import sys
import time
from lora import *

from PIL import Image, ImageDraw, ImageFont
from papirus import Papirus

WHITE = 1
BLACK = 0

lora = LoRa()
lora.open()
lora.run()

papirus = Papirus()

font_size = 16
x_offset = 4
y_offset = 2
y_gap = font_size + 2

font = ImageFont.truetype('/usr/share/fonts/truetype/freefont/FreeMono.ttf', font_size)

image = Image.new('1', papirus.size, WHITE)
papirus.display(image)
papirus.update()

image = Image.new('1', papirus.size, WHITE)
draw = ImageDraw.Draw(image)
OldTime = None

while True:
	time.sleep(0.1)

	Position = lora.Position()
	
	if Position['time'] != OldTime:
		OldTime = Position['time']

		draw.rectangle(((0,0),(200,96)), fill="white", outline = "white")
		
		draw.text((x_offset,0*y_gap+y_offset), 'Payload:   ' + Position['id'], font=font, fill=BLACK)
		draw.text((x_offset,1*y_gap+y_offset), 'Time:      ' + Position['time'], font=font, fill=BLACK)
		draw.text((x_offset,2*y_gap+y_offset), 'Latitude:  ' + "%.5f" % Position['lat'], font=font, fill=BLACK)
		draw.text((x_offset,3*y_gap+y_offset), 'Longitude: ' + "%.5f" % Position['lon'], font=font, fill=BLACK)
		draw.text((x_offset,4*y_gap+y_offset), 'Altitude:  ' + ("%.f" % Position['alt']).rjust(7) + 'm', font=font, fill=BLACK)
		
		papirus.display(image)
		
		if Position['time'][6:8] == '30':
			papirus.update()
		else:
			papirus.partial_update()

