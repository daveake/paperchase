from lora import *
import time

print("Creating LoRa object ...")
lora = LoRa();

print("Open LoRa ...")
lora.open()
print("LoRa open OK")

print("LoRa thread running")
lora.run()

while 1:
	sleep(1)
