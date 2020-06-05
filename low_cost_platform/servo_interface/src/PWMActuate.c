/** @brief File used to send PWM signals to the servo motors on the 
 *			platform to actuate.
 * 
 *  @author Joon You Tan <jtan0026@student.monash.edu>
 */

#include <wiringPi.h>
#include <softPwm.h>

#include <errno.h>
#include <stdio.h>
#include <stdlib.h>

// Parameters for the GPIO:
const int PWM_pin = 1; 			//GPIO 1, pin 18 on raspberry pi sheet
int iter;

int main (void)
{	
	if(wiringPiSetup() == -1)
	{
		return 1;
	}
	
	// Create a pin in which has 20ms pulse cycle with 300 steps:
	if (softPwmCreate(PWM_pin, 0, 200) != 0)
	{
		return 2;
	}
	
	while(1)
	{
		// Set the PWM signal to be 
		for (iter = 5; iter < 30; iter++)
		{
			softPwmWrite(PWM_pin, iter);
			delayMicroseconds(125000);
		}
	}
	
	printf("This has been executed.");
	
	return 0;
}
