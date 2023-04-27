/*
 * MQ9.c
 *
 *  Created on: Apr 22, 2023
 *      Author: DELL
 */

#include "MQ9.h"
float Ratio;
float Int_to_Volt(uint32_t value){
	return (value/4098.0)*VOLT_INPUT;
}

float ReadMQ9(ADC_HandleTypeDef*adc){
	HAL_ADC_Start(adc);
	HAL_ADC_PollForConversion(adc,100);
	uint32_t value=HAL_ADC_GetValue(adc);
	HAL_ADC_Stop(adc);
	float valueVolt=Int_to_Volt(value);
	float Rs=(VOLT_INPUT-valueVolt)/valueVolt;
	float ratio=Rs/R0;
	Ratio=ratio;
	return ratio;
}

uint8_t str1[50];
void SendValueMQ9(UART_HandleTypeDef*huart,uint8_t seq){
	//Send ratio
	int Int_part=(int)Ratio;
	float decimal_part= Ratio-Int_part;
	int Decimal_part=(int)(decimal_part*100);
	/////////////////////////0

	//Send safety signal
//	int Int_part=Ratio>=DANGER_RATIO;
//	int Decimal_part=0;
	//////////////////////

	uint16_t check_sum=seq+Int_part+Decimal_part+2;
	HAL_UART_Transmit(huart, str1,
		sprintf(str1,"!%u:%u:%u:G:%u:%u:%u#",seq, 1 , 1, Int_part, Decimal_part,check_sum), 100);
}
