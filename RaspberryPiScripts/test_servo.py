## @package servo_api
#  Extended package for linking the wiringPi library to Python

import wiringpi

# Define variables here
OUTPUT = 1
TEST_SIGNAL = 9
TEST_PIN = 1

# Setup and init raspberry Pi:
wiringpi.wiringPiSetup()
wiringpi.pinMode(TEST_PIN, OUTPUT)

wiringpi.softPwmCreate(TEST_PIN, 0, 200)

while True:
    wiringpi.softPwmWrite(TEST_PIN, TEST_SIGNAL)
    wiringpi.delay(1)
