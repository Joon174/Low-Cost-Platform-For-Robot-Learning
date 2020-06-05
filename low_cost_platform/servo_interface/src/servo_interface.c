/****************************************************************************
 *  Copyright (C) Monash University Clayton, All Rights Reserved	        *
 * 																			*
 *  @author Joon You Tan													*
 *                                                                          *
 *  Unauthorized copying of this file, via any medium is strictly           *
 *  prohibited.  The contents of this file are proprietary and confidential *
 ****************************************************************************/
#include "servo_interface.h"

int initServos(int *servoPins)
{
	return (softPwmCreate(*servoPins, 0, 200) != 0)
}

void actuateServo(uint8_t *servoPin, uint8_t *pwmSignal)
{
	softPwmWrite(*servoPin, *pwmSignal);
	delayMicroseconds(125000);
}
