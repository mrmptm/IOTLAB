/*
 * ErrorController.h
 *
 *  Created on: Apr 13, 2023
 *      Author: DELL
 */

#ifndef INC_CONTROLLER_H_
#define INC_CONTROLLER_H_

#include "main.h"
#include "SoftwareTimer.h"
#include "DHT12.h"
#include "MQ9.h"
#include <stdio.h>
#include "scheduler.h"


//States
#define WAIT_REQ 1
#define WAIT_ACK 2
#define ABORT_RESEND 3
#define TIMEOUT_ACK 1000

#define READ_SENSOR 1
#define NONE 0
#define ABORT 2

#define HUMID_TEMP 0
#define MQ9 1

typedef struct{
	I2C_HandleTypeDef hi2c;
	UART_HandleTypeDef huart;
	ADC_HandleTypeDef adc;
} Connectivity;
typedef struct {
	uint8_t req;
	uint8_t type;
	uint8_t seq;
	uint8_t failLimit;
	uint8_t ack;
	uint8_t check_sum;
} Message;

void ControllerInit(Connectivity conn);
void processMessage(Message msg);
void ResendMessage();
void SendValue(uint8_t type, uint8_t seq);

#endif /* INC_CONTROLLER_H_ */
