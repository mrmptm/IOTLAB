/*
 * task.c
 *
 *  Created on: Apr 9, 2023
 *      Author: DELL
 */

#include "task.h"
void TurnOn();
void TurnOff();
void TurnOn(){
	HAL_GPIO_WritePin(LED_GPIO_Port, LED_Pin, 1);
	SCH_Add_Task(TurnOff, 1000, 0);
}
void TurnOff(){
	HAL_GPIO_WritePin(LED_GPIO_Port, LED_Pin, 0);
	SCH_Add_Task(TurnOn, 1000, 0);
}
void ToggleLed(){
	SCH_Add_Task(TurnOff, 0, 0);
}


