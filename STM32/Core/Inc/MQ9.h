/*
 * MQ9.h
 *
 *  Created on: Apr 22, 2023
 *      Author: DELL
 */

#ifndef INC_MQ9_H_
#define INC_MQ9_H_

#include "main.h"
#define VOLT_INPUT 3.3
#define R0 0.3

#define DANGER_RATIO 3.5
float ReadMQ9(ADC_HandleTypeDef*adc);

void SendValueMQ9(UART_HandleTypeDef*huart,uint8_t seq);

#endif /* INC_MQ9_H_ */
