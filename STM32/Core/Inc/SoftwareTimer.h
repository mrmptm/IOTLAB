/*
 * SoftwareTimer.h
 *
 *  Created on: Sep 28, 2022
 *      Author: DELL
 */

#ifndef SOFTWARETIMER_H_
#define SOFTWARETIMER_H_

extern int counter1;
extern int timer1_flag;
void setTimer1(int duration);  //millisecond
extern int counter2;
extern int timer2_flag;
void setTimer2(int duration);  //millisecond

extern int counter3;
extern int timer3_flag;
void setTimer3(int duration);  //millisecond
extern int counter4;
extern int timer4_flag;
void setTimer4(int duration);  //millisecond
void TimerRun();

#endif /* SOFTWARETIMER_H_ */
