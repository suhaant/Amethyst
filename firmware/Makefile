# PulsePatch firmware.
#   make test       build the core against a simulated board and run the tests on this computer
#   make arm-check  compile the core for the nRF52832 (Cortex-M4F) to prove it builds for the target
CC      ?= cc
CFLAGS  := -std=c11 -Wall -Wextra -Werror -pedantic -Icore -Itests
CORE    := core/tmp117.c core/impedance.c core/ph.c core/therapy.c core/telemetry.c core/app.c
ARM_CC  := arm-none-eabi-gcc
ARM_FLAGS := -mcpu=cortex-m4 -mthumb -mfloat-abi=hard -mfpu=fpv4-sp-d16 -std=c11 -Os -Wall -Wextra -Werror -ffreestanding -Icore

.PHONY: test arm-check clean

test: build/test_runner
	./build/test_runner

build/test_runner: $(CORE) tests/fake_hal.c tests/test_main.c $(wildcard core/*.h tests/*.h)
	mkdir -p build
	$(CC) $(CFLAGS) -o $@ $(CORE) tests/fake_hal.c tests/test_main.c

arm-check:
	mkdir -p build/arm
	for f in $(CORE); do $(ARM_CC) $(ARM_FLAGS) -c $$f -o build/arm/$$(basename $$f .c).o || exit 1; done
	arm-none-eabi-size build/arm/*.o

clean:
	rm -rf build
