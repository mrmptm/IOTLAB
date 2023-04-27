/*
 * DHT12.c
 *
 *  Created on: Apr 13, 2023
 *      Author: DELL
 */

#include "DHT12.h"

int16_t tempInt=0;
uint8_t temp_float=0;
uint8_t humid_int=0;
uint8_t humid_float=0;
uint8_t checksum;

uint8_t buf[5];
HAL_StatusTypeDef ReadDHT(I2C_HandleTypeDef*hi2c){
	HAL_StatusTypeDef ret;
	ret=HAL_I2C_Master_Transmit(hi2c, DHT12, 0x00, 1, 1000);
	if(ret==HAL_OK){
		ret=HAL_I2C_Master_Receive(hi2c, DHT12, buf, 5, 1000);
		if(ret==HAL_OK){
			checksum=buf[4];
			if(buf[0]+buf[1]+buf[2]+buf[3]==buf[4]){
				humid_int=buf[0];
				humid_float=buf[1];
				uint8_t temp_int=buf[2];
				temp_float=buf[3];
				if(temp_float>=0x80){  //negative temperature
					tempInt=(-1)*temp_int;
				}else tempInt=temp_int;
				temp_float=(temp_float<<1)>>1;
			}else return !HAL_OK;
		}
	}
	return ret;
}
uint8_t str[50];
void SendValueDHT(UART_HandleTypeDef*huart,uint8_t seq){
	//SEND TEMP
	uint16_t check_sum=seq+tempInt+temp_float+3;
	HAL_UART_Transmit(huart, str,
		sprintf(str,"!%u:%u:%u:T:%d:%u:%u#",seq, 1, 2,tempInt, temp_float,check_sum), 100);
	//SEND HUMIDITY
	check_sum=seq+humid_int+humid_float+4;
	HAL_UART_Transmit(huart, str,
		sprintf(str,"!%u:%u:%u:H:%u:%u:%u#",seq, 2 , 2, humid_int, humid_float,check_sum), 100);
}

