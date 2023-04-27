/*
 * DHT12.h
 *
 *  Created on: Apr 13, 2023
 *      Author: DELL
 */

#ifndef INC_DHT12_H_
#define INC_DHT12_H_

#include "main.h"
#include <stdio.h>
#define DHT12 0xB8

HAL_StatusTypeDef ReadDHT(I2C_HandleTypeDef*hi2c);
void SendValueDHT(UART_HandleTypeDef*huart, uint8_t seq);

#endif /* INC_DHT12_H_ */
