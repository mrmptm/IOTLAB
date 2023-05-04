/*
 * ErrorController.c
 *
 *  Created on: Apr 13, 2023
 *      Author: DELL
 */

#include <Controller.h>
uint8_t cseq=0;
uint8_t cack=0;
uint8_t timeOutCount=0;
uint8_t timeOutLimit;
uint8_t type;

I2C_HandleTypeDef hi2c;
UART_HandleTypeDef huart;
ADC_HandleTypeDef adc;
uint8_t response[50];

uint8_t state=0;
uint8_t isOK(Message msg){
	return msg.req+msg.seq+msg.failLimit+msg.ack==msg.check_sum;
}

void processMessage(Message msg){
	switch(state){
		case WAIT_REQ:
			if(isOK(msg)){ 	 //data transfered from gateway correctly
				if(msg.req==READ_SENSOR){  //Gateway request read sensor
					if(msg.type==HUMID_TEMP){
						HAL_StatusTypeDef ret;
						type=msg.type;
						ret=ReadDHT(&hi2c);  //Read from sensor
						if(ret==HAL_OK){ //Read success
							HAL_GPIO_TogglePin(LED_GPIO_Port, LED_Pin);
							//Send value to gateway
							cseq=msg.seq;
							SendValue(msg.type,msg.seq);
							SCH_Add_Task(ResendMessage, TIMEOUT_ACK, TIMEOUT_ACK);
							timeOutCount=0;
							timeOutLimit=msg.failLimit;
							state=WAIT_ACK;
						}
					}else if(msg.type==MQ9){
						type=msg.type;
						cseq=msg.seq;
						ReadMQ9(&adc);
						SendValueMQ9(&huart, msg.seq);
						SCH_Add_Task(ResendMessage, TIMEOUT_ACK, TIMEOUT_ACK);
						timeOutCount=0;
						timeOutLimit=msg.failLimit;
						state=WAIT_ACK;
					}
				}
			}else{ //data transfered from gateway incorrectly
				//Ask gateway to re-send
				HAL_UART_Transmit(&huart, response, sprintf(response,"!Re-send#"), 500);
			}
			break;
		case WAIT_ACK:
			if(isOK(msg)){  //Data transfered correctly
				if((msg.req==NONE) && msg.ack){  //receive ACK, back to WAIT_REQEST
					state=WAIT_REQ;
					SelfDestruct(ResendMessage);
				}else if(msg.ack==0 || msg.req==READ_SENSOR){ //previous data error or gateway didn't receive data
					SendValue(msg.type, cseq);
					SCH_Add_Task(ResendMessage, TIMEOUT_ACK, TIMEOUT_ACK); //Reset timer for re-send
					timeOutCount=0;
				}else if(msg.req==ABORT){
					SelfDestruct(ResendMessage);
					state=WAIT_REQ;
				}
			}else{  //Data transfered incorrectly
				HAL_UART_Transmit(&huart, response, sprintf(response,"!Re-send#"), 500);
				SCH_Add_Task(ResendMessage, TIMEOUT_ACK, TIMEOUT_ACK); //Reset timer for re-send
			}
			break;
	}
}


void ResendMessage(){
	timeOutCount++;
	if(timeOutCount>timeOutLimit){
		HAL_UART_Transmit(&huart, response, sprintf(response,"!Abort:%u#",cseq), 500);
		SelfDestruct(ResendMessage);
		state=WAIT_REQ;
		return;
	}
	SendValue(type, cseq);
}
void ControllerInit(Connectivity conn){
	hi2c=conn.hi2c;
	huart=conn.huart;
	adc=conn.adc;
	state=WAIT_REQ;
}

void SendValue(uint8_t type, uint8_t seq){
	if(type==HUMID_TEMP){
		SendValueDHT(&huart, seq);
	}else if(type==MQ9){
		SendValueMQ9(&huart, seq);
	}
}





