/****************************************************************************
 *  Copyright (C) Monash University Clayton, All Rights Reserved	        *
 *                                                                          *
 *  Unauthorized copying of this file, via any medium is strictly           *
 *  prohibited.  The contents of this file are proprietary and confidential *
 ****************************************************************************/

/** 
 * Import necessary library for testing 
 */
#include "CppUTest/Testharness.h"

/** 
 * Include all custom libraries to be used in test 
 */
extern "C"
{
	#include <wiringPi.h>
	#include <softPwm.h>
	#include "servo_interface.h"
}

TEST_GROUP(servo_interface)
{
	uint8_t servoPin;
	uint8_t pwmSignal; 
	
	/** 
	 * Setup variables for testing 
	 */
	void setup()
	{
		servoPin = 1;
		pwmSignal = 12;
	}
	
	/** 
	 * Terminates in a clean manner 
	 */ 
	void teardown()
	{
	}
};

TEST(servo_interface, servo_init)
{
	result = initServos();
	CHECK_EQUAL(result, 0);
}

TEST(servo_interface, servo_actuate_single)
{
	actuateServo(servoPin, pwmSignal);
}

TEST(servo_interface, servo_actutate_multiple)
{
	uint8_t servoPin2, pwmSignal2;
	actuateServo(servoPin2, pwmSignal2);
}
