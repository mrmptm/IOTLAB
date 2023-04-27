/*
 * SoftwareTimer.c
 *
 *  Created on: Sep 28, 2022
 *      Author: DELL
 */
#include <SoftwareTimer.h>
int counter1;
int timer1_flag;

int counter2;
int timer2_flag;

int counter3;
int timer3_flag;

int counter4;
int timer4_flag;

int TIMER_CYCLE=10;

void setTimer1(int duration){
	counter1=duration/TIMER_CYCLE;
	timer1_flag=0;
}

void setTimer2(int duration){
	counter2=duration/TIMER_CYCLE;
	timer2_flag=0;
}

void setTimer3(int duration){
	counter3=duration/TIMER_CYCLE;
	timer3_flag=0;
}

void setTimer4(int duration){
	counter4=duration/TIMER_CYCLE;
	timer4_flag=0;
}

void TimerRun(){
	if(counter1>0){
		counter1--;
		if(counter1<=0){
			timer1_flag=1;
		}
	}

	if(counter2>0){
		counter2--;
		if(counter2<=0){
			timer2_flag=1;
		}
	}

	if(counter3>0){
		counter3--;
		if(counter3<=0){
			timer3_flag=1;
		}
	}

	if(counter4>0){
		counter4--;
		if(counter4<=0){
			timer4_flag=1;
		}
	}
}


