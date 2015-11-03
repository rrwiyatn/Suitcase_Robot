#include
import time
from imgproc import *
import RPi.GPIO as GPIO
from time import sleep

#setup
width = 160
height = 120

GPIO_TRIGGER = 36
GPIO_ECHO = 38

#Motor1 (Left)
MotorL_forward = 16 #(forward)
MotorL_reverse = 18 #(reverse)
MotorL_enable  = 22 #(ON/OFF)

#Motor2 (Right)
MotorR_reverse = 11 #(forward)
MotorR_forward = 13 #(reverse)
MotorR_enable  = 15 #(ON/OFF)

#variables
cal_R = 0
cal_G = 0
cal_B = 0
distance = 0
speedR = 0
speedL = 0
count = 837
dir = 2

#owner needs to stand in front of the camera when the robot starts
def calibrate(my_camera, count, cal_R, cal_G, cal_B):
	print ("Adjusting...")
	abort_time = 8
	start = time.time()
	while True:
		elapsed = time.time() - start
		if elapsed >= abort_time:
			break
		my_image = my_camera.grabImage()
		for y in range (21,54):
	       #{
			for x in range (66,97):
		       #{
				if (x>=66 and x<=95 and y==21):
					my_image[x,y] = 255,0,0
				elif (x==66 and y>=21 and y<=53):
					my_image[x,y] = 255,0,0
				elif (x==95 and y>=21 and y<=53):
					my_image[x,y] = 255,0,0
				elif (x>=66 and x<=95 and y==53):
					my_image[x,y] = 255,0,0
		       #}
	       #}
		my_view = Viewer(my_image.width, my_image.height, "Calibration")
		my_view.displayImage(my_image)
	print ("Calibrating...")
	for y in range (22,53):
       #{
		for x in range (67,96):
	       #{
			red, green, blue = my_image[x,y]
			cal_R = cal_R + red
			cal_G = cal_G + green
			cal_B = cal_B + blue
	       #}
       #}
	cal_R = cal_R/count
	cal_G = cal_G/count
	cal_B = cal_B/count
	time.sleep(3)
	print "ROBOT READY" 
	return (cal_R,cal_G,cal_B)
	
	
#To check where the position of the owner is
def checkTop(my_camera, cal_R, cal_G, cal_B, dir, my_image): #3 regions
	region_red_L = 0
	region_green_L = 0 
	region_blue_L = 0
	region_red_M = 0
	region_green_M = 0
	region_blue_M = 0
	region_red_R = 0
 	region_green_R = 0
	region_blue_R = 0
	
	response_L = 0
	response_M = 0 
	response_R = 0

	#Region 1
	for i in range (95,101):
       #{
		for j in range (0, 53):
	       #{
			red, green, blue = my_image[j,i]
			region_red_L = region_red_L + red
			region_green_L = region_green_L + green
			region_blue_L = region_blue_L + blue
	       #}
       #}
	#Region 2
	for i in range (95,101):
		for j in range (53, 107):
			red, green, blue = my_image[j,i]
			region_red_M = region_red_M + red
			region_green_M = region_green_M + green
			region_blue_M = region_blue_M + blue
	#Region 3
	for i in range (95,101):
		for j in range (107, 159):
			red, green, blue = my_image[j,i]
			region_red_R = region_red_R + red
			region_green_R = region_green_R + green
			region_blue_R = region_blue_R + blue
	
	region_red_L= region_red_L
	region_green_L= region_green_L
	region_blue_L= region_blue_L
	
	region_red_M= region_red_M
	region_green_M= region_green_M
	region_blue_M= region_blue_M

	region_red_R= region_red_R
	region_green_R= region_green_R
	region_blue_R= region_blue_R

	response_L = abs(cal_R - region_red_L) + abs(cal_G - region_green_L) + abs(cal_B - region_blue_L)
	response_M = abs(cal_R - region_red_M) + abs(cal_G - region_green_M) + abs(cal_B - region_blue_M)
	response_R = abs(cal_R - region_red_R) + abs(cal_G - region_green_R) + abs(cal_B - region_blue_R)
	
	if (response_L < response_M) and (response_L < response_R):
		dir = 1
	elif (response_M < response_L) and (response_M < response_R):
		dir = 2
	elif (response_R < response_L) and (response_R < response_M):
		dir = 3
	return dir
	
def move(MotorR_forward, MotorL_forward, speedR, speedL):
	for i in range(0,255):
		if i>= speedR:
			GPIO.output(MotorR_forward, GPIO.LOW)
		if i>= speedL:
			GPIO.output(MotorL_forward, GPIO.LOW)
		sleep(0.0004)

def get_distance(GPIO_TRIGGER,GPIO_ECHO,distance):
	GPIO.output(GPIO_TRIGGER, False)
	time.sleep(0.00001)
	GPIO.output(GPIO_TRIGGER, True)
	time.sleep(0.00001)
	GPIO.output(GPIO_TRIGGER, False)
	start = time.time()
	while GPIO.input(GPIO_ECHO)==0:
  		start = time.time()
	while GPIO.input(GPIO_ECHO)==1:
  		stop = time.time()
	distance = (stop - start) * 17000
	return distance

def adjust_speed(distance, speedR, speedL, dir):
	if distance <= 50:
		GPIO.output(MotorR_forward, GPIO.LOW)
		GPIO.output(MotorL_forward, GPIO.LOW)
		speedR = 0
		speedL = 0
	elif distance >= 250:
		GPIO.output(MotorR_forward, GPIO.LOW)
		GPIO.output(MotorL_forward, GPIO.LOW)
		speedR = 0
		speedL = 0
	elif dir == 1 and distance > 50: #turn left
		GPIO.output(MotorR_forward, GPIO.HIGH)
		GPIO.output(MotorL_forward, GPIO.HIGH)
		speedR = 255 
		speedL = 230
	elif dir == 3 and distance > 50: #turn right
		GPIO.output(MotorR_forward, GPIO.HIGH)
		GPIO.output(MotorL_forward, GPIO.HIGH)
		speedR = 250
		speedL = 255 
	elif dir == 2 and distance > 50:
		GPIO.output(MotorR_forward, GPIO.HIGH)
		GPIO.output(MotorL_forward, GPIO.HIGH)
		speedR = 255
		speedL = 255
	elif distance > 50 and distance <250:
		GPIO.output(MotorR_forward, GPIO.HIGH)
		GPIO.output(MotorL_forward, GPIO.HIGH)
		speedR = 200
		speedL = 200
	return (speedR, speedL)
	
def stop(MotorR_enable, MotorL_enable):
	GPIO.output(MotorR_enable, GPIO.LOW)
	GPIO.output(MotorL_enable, GPIO.LOW)

def end():
	print "Ending program..."
	stop(MotorR_enable, MotorL_enable)
	GPIO.cleanup()
	
my_camera = Camera(160,120)
#starts calibration
cal_R,cal_G,cal_B = calibrate(my_camera, count, cal_R, cal_G, cal_B)

GPIO.setmode(GPIO.BOARD)
GPIO.setup(GPIO_TRIGGER,GPIO.OUT)
GPIO.setup(GPIO_ECHO,GPIO.IN)

GPIO.setup(MotorR_forward, GPIO.OUT)
GPIO.setup(MotorR_reverse, GPIO.OUT)
GPIO.setup(MotorR_enable, GPIO.OUT)

GPIO.output(MotorR_reverse, GPIO.LOW)
GPIO.output(MotorR_enable, GPIO.HIGH)

GPIO.setup(MotorL_forward, GPIO.OUT)
GPIO.setup(MotorL_reverse, GPIO.OUT)
GPIO.setup(MotorL_enable, GPIO.OUT)

GPIO.output(MotorL_reverse, GPIO.LOW)
GPIO.output(MotorL_enable, GPIO.HIGH)
z = 0
try:
	while True:
		#grab image
		my_image = my_camera.grabImage()
		my_view = Viewer(my_image.width, my_image.height, "Calibration")
		my_view.displayImage(my_image)
		dir= checkTop(my_camera, cal_R, cal_G, cal_B, dir, my_image)
		print "Dir = %.1f" %dir
		if z%5 == 0:
			distance = get_distance(GPIO_TRIGGER,GPIO_ECHO,distance)
			print "Distance = %.1f" %distance
		speedR,speedL=adjust_speed(distance, speedR, speedL, dir)
		move(MotorR_forward, MotorL_forward, speedR, speedL)
		z=z+1
	
except KeyboardInterrupt:
	end()
