/****************************************************************************
 *  Copyright (C) Monash University Clayton, All Rights Reserved	        *
 * 																			*
 *  @author Joon You Tan													*
 *                                                                          *
 *  Unauthorized copying of this file, via any medium is strictly           *
 *  prohibited.  The contents of this file are proprietary and confidential *
 ****************************************************************************/
 
 #include <wiringPi.h>
 #include <softPwm.h>
 
typedef struct robotConfig *setupConfig;
 
void actuateServo(uint8_t *servoPin, uint8_t *pwmSignal);
