# grovepi + grove RGB LCD module
#http://www.seeedstudio.com/wiki/Grove_-_LCD_RGB_Backlight
#
# Just supports setting the backlight colour, and
# putting a single string of text onto the display
# Doesn't support anything clever, cursors or anything


import time,sys
import RPi.GPIO as GPIO
import smbus
import pickle
import os.path
import os
import subprocess
import re
import datetime


DISPLAY_RGB_ADDR=0x62
DISPLAY_TEXT_ADDR=0x3e

# use the bus that matches your raspi version
rev = GPIO.RPI_REVISION
if rev == 2 or rev == 3:
    bus = smbus.SMBus(1)
else:
    bus = smbus.SMBus(0)

# set backlight to (R,G,B) (values from 0..255 for each)
def setRGB(r,g,b):
    bus.write_byte_data(DISPLAY_RGB_ADDR,0,0)
    bus.write_byte_data(DISPLAY_RGB_ADDR,1,0)
    bus.write_byte_data(DISPLAY_RGB_ADDR,0x08,0xaa)
    bus.write_byte_data(DISPLAY_RGB_ADDR,4,r)
    bus.write_byte_data(DISPLAY_RGB_ADDR,3,g)
    bus.write_byte_data(DISPLAY_RGB_ADDR,2,b)

# send command to display (no need for external use)    
def textCommand(cmd):
    bus.write_byte_data(DISPLAY_TEXT_ADDR,0x80,cmd)

# set display text \n for second line(or auto wrap)     
def setText(text):
  textCommand(0x01) # clear display
  time.sleep(0.05)
  textCommand(0x08|0x04) # display on, no cursor
  textCommand(0x28) # 2 lines
  time.sleep(0.05)
  count = 0
  row=0
  for c in text:
    if c=='\n':
        count=0
        row=1
        textCommand(0xc0)
        continue
    if count==16 and row==0:
        textCommand(0xc0)
        row+=1
    count+=1
    bus.write_byte_data(DISPLAY_TEXT_ADDR,0x40,ord(c))


# example code

if __name__=="__main__":
    while True:
        try:
            while True:
                cmd = ['sudo','python','./scd30-once.py'] 
                try:
                    out = subprocess.check_output(cmd)
                    split_out = re.split(' |\n',out)
                    time_now = str(datetime.datetime.now())
                    co2 = float(split_out[1])
                    temp = float(split_out[3])
                    humidity = float( split_out[5])
                    print(temp, co2, humidity)
                    #setRGB(0,0,255)
                    setText('T/H:%.1fC/%.1f%% \nCO2:%.1f PPM' %(temp, humidity, co2))
                    if co2 < 600:
                        setRGB(0,255,0) # set BL to green
                    if co2 >= 600:
                        setRGB(255,255,0) # set BL to yellow
                    if co2 >= 800:
                        setRGB(255,0,0) # set BL to red
                except:
                    print('Return error!')
                time.sleep(2)
        
        except IndexError:
            print("  Unable to read")
        except KeyboardInterrupt:
            print("  Exiting by user")
            sys.exit(0)
    #setText("CO2:",co2)
    #setRGB(0,0,255)
    #for c in range(0,255):
    #  setRGB(c,255-c,0)
    #  time.sleep(0.01)
    #setRGB(0,0,255)
    #setText("Bye bye!")



