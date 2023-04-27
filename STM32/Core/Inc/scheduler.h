/*
 * scheduler.h
 *
 *  Created on: Nov 17, 2022
 *      Author: DELL
 */

#ifndef INC_SCHEDULER_H_
#define INC_SCHEDULER_H_
#include "main.h"
#define TIMER_CYCLE 10
#define MAX_TASK 10
#define MAX_TASKID 0

#define ERROR_SCH_WAITING_FOR_SLAVE_TO_ACK 1
#define ERROR_SCH_WAITING_FOR_START_COMMAND_FROM_MASTER 2
#define ERROR_SCH_ONE_OR_MORE_SLAVES_DID_NOT_START 3
#define ERROR_SCH_LOST_SLAVE 4
#define ERROR_SCH_CAN_BUS_ERROR 5
#define ERROR_I2C_WRITE_BYTE_AT24C64 6
#define ERROR_SCH_TOO_MANY_TASKS 7
#define ERROR_SCH_CANNOT_DELETE_TASK 8

//#define SCH_REPORT_ERRORS
#ifdef SCH_REPORT_ERRORS
#define Error_Port PORTA
#endif

typedef struct {
	void(*ptask)(void);
	int32_t Delay;
	uint32_t Runme;
	uint32_t Period;
	uint32_t TaskID;
} sTask;
extern unsigned char Error_code;
void SCH_Init();
int SCH_Add_Task(void(*func)(), int32_t delay, uint32_t Period);
void SCH_Update();
int number_current_task();
void SCH_Dispatch();
void SCH_Delete_Task(int idx);
void SelfDestruct(void(*func)());
#endif /* INC_SCHEDULER_H_ */
