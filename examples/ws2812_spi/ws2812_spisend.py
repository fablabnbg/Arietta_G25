#!/usr/bin/python
#
# (c) 2014,2015, Juergen Weigert, juewei@fabfolk.com
# Distribute under GPL-2.0 or ask.
#
#
# Example program to drive 8 WS2812 RGB Leds with the SPI interface
# of an Arietta board.
#
# This also understands the hyperion protocol for color changes via 
# your android smart phone.
#
# Hardware wiring:
#
# Pin J4.8 (SPI1 MOSI) -> Pin 1 + Pin 2 of a 74HCT02, 
# LED chain input is at Pin 3 of 74HTC02,
# Pin J4.9 (GND) -> Pin 7 of 74HTC02 + GND of LED chain
# Pin J4.1 (5V)  -> Pin 14 of 74HTC02 + 5V of LED chain.
#
# Kernel preparation:
# http://www.acmesystems.it/pinout_arietta
# -> click on SPI bus [x] SPI
# -> [Generate acme-arietta.dtb]
#
# CAUTION: it does not work with the stock 3.14.x kernel. 
#          You need to compile a 3.16.1 kernel, as demonstrated in
#          http://www.acmesystems.it/compile_linux_3_16
#
# Copy the downloaded file to your SDcard, according to the online instructions.

import posix
import struct
from ctypes import addressof, create_string_buffer, sizeof, string_at
from fcntl import ioctl
from spi_ctypes import *
import sys, time
import hyperion

nleds=50		# max 341
sleeptime=0.0001/nleds
spidev="/dev/spidev32766.2"

if (len(sys.argv) > 1):
  try:
    nleds = int(sys.argv[1])
  except:
    print "Need a numeric parameter: number of LEDs"

print "nleds=%d" % nleds

class spibus_ws2812():
	def __init__(self,device,nleds):
		self.fd=None
		self.write_buffer=create_string_buffer(nleds*3*4)
		self.read_buffer=create_string_buffer(nleds*3*4)

			# speed_hz=5000000,
			# speed_hz=3500000,  # worked once
			# speed_hz=2550000,  # 1.6us @ 4bit per bit
			# speed_hz=3500000,    # 1.2us @ 4bit per bit
		self.ioctl_arg = spi_ioc_transfer(
			tx_buf=addressof(self.write_buffer),
			rx_buf=addressof(self.read_buffer),
			len=1,
			delay_usecs=0,
			speed_hz=3500000,
			bits_per_word=8,
			cs_change = 0,
		)

		self.fd = posix.open(device, posix.O_RDWR)
		ioctl(self.fd, SPI_IOC_RD_MODE, " ")
		ioctl(self.fd, SPI_IOC_WR_MODE, struct.pack('I',0))

	def send(self,len):
		self.ioctl_arg.len=len
		ioctl(self.fd, SPI_IOC_MESSAGE(1),addressof(self.ioctl_arg))

	def set_led(self, j, rgb):
		doublebit = [ 
	    		# spi sends the msb first, and we invert all
	    		0x77, 	# 111.111.	0 0
	    		0x71, 	# 111.1...	0 1
	    		0x17, 	# 1...111.	1 0
	    		0x11, 	# 1...1...	1 1
	  	]

		# darkest colors
		# gn = [ 0x77, 0x77, 0x77, 0x71,  0x77, 0x77, 0x77, 0x77,   0x77, 0x77, 0x77, 0x77 ]
		# rd = [ 0x77, 0x77, 0x77, 0x77,  0x77, 0x77, 0x77, 0x71,   0x77, 0x77, 0x77, 0x77 ]
		# bl = [ 0x77, 0x77, 0x77, 0x77,  0x77, 0x77, 0x77, 0x77,   0x77, 0x77, 0x77, 0x71 ]

		i = j * 12
		r,g,b = rgb
		self.write_buffer[i+ 0] = chr(doublebit[(g>>6) & 3])
		self.write_buffer[i+ 1] = chr(doublebit[(g>>4) & 3])
		self.write_buffer[i+ 2] = chr(doublebit[(g>>2) & 3])
		self.write_buffer[i+ 3] = chr(doublebit[(g>>0) & 3])

		self.write_buffer[i+ 4] = chr(doublebit[(r>>6) & 3])
		self.write_buffer[i+ 5] = chr(doublebit[(r>>4) & 3])
		self.write_buffer[i+ 6] = chr(doublebit[(r>>2) & 3])
		self.write_buffer[i+ 7] = chr(doublebit[(r>>0) & 3])

		self.write_buffer[i+ 8] = chr(doublebit[(b>>6) & 3])
		self.write_buffer[i+ 9] = chr(doublebit[(b>>4) & 3])
		self.write_buffer[i+10] = chr(doublebit[(b>>2) & 3])
		self.write_buffer[i+11] = chr(doublebit[(b>>0) & 3])


#Open the SPI bus 0
spi_leds = spibus_ws2812(spidev,nleds)

rgb = [
	[
	  [ 0 ,  1,  0],
	  [ 1 ,  1, 10],
	  [ 1 ,  1, 33],
	  [ 33, 33,  0],
	  [ 33,  0,  0],
	  [ 0 , 33,  0],
	  [ 33,  0, 33],
	  [ 33,  0,  0]
	],
	[
	  [ 0,  1,  0],
	  [ 0,  1, 20],
	  [ 0,  1, 66],
	  [ 0, 66,  0],
	  [ 0,  0,  0],
	  [ 0, 66,  0],
	  [ 0,  0, 66],
	  [ 0,  0,  0]
	],
	[
	  [ 1 ,  0,  0],
	  [ 10 , 0,  0],
	  [ 40 , 0,  1],
	  [ 100, 0,  0],
	  [ 100, 0,  0],
	  [ 40 , 0,  0],
	  [ 10,  0,  0],
	  [ 1,   0,  0]
	],
	[
	  [ 0, 0,  1],
	  [ 0, 1,  1],
	  [ 0, 1,  0],
	  [ 1, 1,  0],
	  [ 1, 1,  0],
	  [ 0, 1,  0],
	  [ 0, 1,  1],
	  [ 0, 0,  1]
	],
	[
	  [ 0 ,  1,   0],
	  [ 1 ,  1,  10],
	  [ 1 ,  1, 255],
	  [ 255, 255, 0],
	  [ 255, 0,   0],
	  [ 0 , 255,  0],
	  [ 255, 0, 255],
	  [ 255, 0,   0]
	],
	[
	  [ 255, 255, 255],
	  [ 255, 255, 255],
	  [ 255, 255, 255],
	  [ 255, 255, 255],
	  [ 255, 255, 255],
	  [ 255, 255, 255],
	  [ 255, 255, 255],
	  [ 255, 255, 255],
	],
	[
	  [ 255, 25, 255],
	  [ 255, 25, 255],
	  [ 255, 25, 255],
	  [ 255, 25, 255],
	  [ 255, 25, 255],
	  [ 255, 25, 255],
	  [ 255, 25, 255],
	  [ 255, 25, 255],
	]
]

pattern=0
top = len(rgb[pattern])

for x in range(nleds):
  spi_leds.set_led(x, rgb[pattern][x%top])

hyp = hyperion.server()

blue = [0,0,255]

dir=1
x=1
xx=0
while (True):
  spi_leds.send(3*4*nleds)
  spi_leds.set_led(xx, rgb[pattern][x%top])
  if (x <= 0) : dir = 1
  if (x >= nleds-1) : dir = -1
  xx = x
  x += dir
  spi_leds.set_led(x, blue)
  # print x
  if (hyp.poll()):
    new = hyp.color()
    if new: blue = new

    num = hyp.duration()
    num = int(num/1000)
    if num > 341: 
      print "max nleds = 341"
      num = 341
    if num and (num != nleds):
      print "num=", num
      nleds = num
      dir = 1
      x = 1
      xx = 0
      spi_leds = spibus_ws2812(spidev,nleds)
      # sleeptime = 0.1/nleds

    if not new and not num:
      print hyp.json()
      pattern = (pattern + 1) % len(rgb)

  time.sleep(sleeptime)

  
#Shows the 2 byte received in full duplex in hex format
# print hex(ord(spibus0.read_buffer[0]))
# print hex(ord(spibus0.read_buffer[1]))



