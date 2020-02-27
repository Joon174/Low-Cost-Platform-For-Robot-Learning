/****************************************************************************
 *  Copyright (C) Monash University Clayton, All Rights Reserved	        *
 * 																			*
 *  @author Joon You Tan													*
 *                                                                          *
 *  Unauthorized copying of this file, via any medium is strictly           *
 *  prohibited.  The contents of this file are proprietary and confidential *
 ****************************************************************************/

#define MPU6050_ADDRESS 0x68
#define

int initI2C(uint8_t *commPin)
{
	uint8_t *temp;
	*temp = wiringPiI2CSetup(*commPin);
	return checkRC(*temp, "wiringPiI2CSetup");
}

typedef struct 

int readIMU(uint8_t *sensorPin, uint8_t *sensorValue)
{
	return digitalRead();
}
