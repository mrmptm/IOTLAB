################################################################################
# Automatically-generated file. Do not edit!
# Toolchain: GNU Tools for STM32 (10.3-2021.10)
################################################################################

# Add inputs and outputs from these tool invocations to the build variables 
C_SRCS += \
../Core/Src/Controller.c \
../Core/Src/DHT12.c \
../Core/Src/MQ9.c \
../Core/Src/SoftwareTimer.c \
../Core/Src/main.c \
../Core/Src/scheduler.c \
../Core/Src/stm32f4xx_hal_msp.c \
../Core/Src/stm32f4xx_it.c \
../Core/Src/syscalls.c \
../Core/Src/sysmem.c \
../Core/Src/system_stm32f4xx.c \
../Core/Src/task.c 

OBJS += \
./Core/Src/Controller.o \
./Core/Src/DHT12.o \
./Core/Src/MQ9.o \
./Core/Src/SoftwareTimer.o \
./Core/Src/main.o \
./Core/Src/scheduler.o \
./Core/Src/stm32f4xx_hal_msp.o \
./Core/Src/stm32f4xx_it.o \
./Core/Src/syscalls.o \
./Core/Src/sysmem.o \
./Core/Src/system_stm32f4xx.o \
./Core/Src/task.o 

C_DEPS += \
./Core/Src/Controller.d \
./Core/Src/DHT12.d \
./Core/Src/MQ9.d \
./Core/Src/SoftwareTimer.d \
./Core/Src/main.d \
./Core/Src/scheduler.d \
./Core/Src/stm32f4xx_hal_msp.d \
./Core/Src/stm32f4xx_it.d \
./Core/Src/syscalls.d \
./Core/Src/sysmem.d \
./Core/Src/system_stm32f4xx.d \
./Core/Src/task.d 


# Each subdirectory must supply rules for building sources it contributes
Core/Src/%.o Core/Src/%.su: ../Core/Src/%.c Core/Src/subdir.mk
	arm-none-eabi-gcc "$<" -mcpu=cortex-m4 -std=gnu11 -g3 -DDEBUG -DUSE_HAL_DRIVER -DSTM32F411xE -c -I../Core/Inc -I../Drivers/STM32F4xx_HAL_Driver/Inc -I../Drivers/STM32F4xx_HAL_Driver/Inc/Legacy -I../Drivers/CMSIS/Device/ST/STM32F4xx/Include -I../Drivers/CMSIS/Include -O0 -ffunction-sections -fdata-sections -Wall -fstack-usage -MMD -MP -MF"$(@:%.o=%.d)" -MT"$@" --specs=nano.specs -mfpu=fpv4-sp-d16 -mfloat-abi=hard -mthumb -o "$@"

clean: clean-Core-2f-Src

clean-Core-2f-Src:
	-$(RM) ./Core/Src/Controller.d ./Core/Src/Controller.o ./Core/Src/Controller.su ./Core/Src/DHT12.d ./Core/Src/DHT12.o ./Core/Src/DHT12.su ./Core/Src/MQ9.d ./Core/Src/MQ9.o ./Core/Src/MQ9.su ./Core/Src/SoftwareTimer.d ./Core/Src/SoftwareTimer.o ./Core/Src/SoftwareTimer.su ./Core/Src/main.d ./Core/Src/main.o ./Core/Src/main.su ./Core/Src/scheduler.d ./Core/Src/scheduler.o ./Core/Src/scheduler.su ./Core/Src/stm32f4xx_hal_msp.d ./Core/Src/stm32f4xx_hal_msp.o ./Core/Src/stm32f4xx_hal_msp.su ./Core/Src/stm32f4xx_it.d ./Core/Src/stm32f4xx_it.o ./Core/Src/stm32f4xx_it.su ./Core/Src/syscalls.d ./Core/Src/syscalls.o ./Core/Src/syscalls.su ./Core/Src/sysmem.d ./Core/Src/sysmem.o ./Core/Src/sysmem.su ./Core/Src/system_stm32f4xx.d ./Core/Src/system_stm32f4xx.o ./Core/Src/system_stm32f4xx.su ./Core/Src/task.d ./Core/Src/task.o ./Core/Src/task.su

.PHONY: clean-Core-2f-Src

