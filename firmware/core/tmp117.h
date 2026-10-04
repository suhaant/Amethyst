#ifndef TMP117_H
#define TMP117_H

#include <stdint.h>

int32_t tmp117_raw_to_mC(int16_t raw);
int16_t tmp117_mC_to_raw(int32_t mC);
/* Checks the device ID, writes the alert limits and starts continuous conversion with the alert pin in
 * thermostat mode (asserts above high, releases below low). Returns 0, or non-zero if the sensor is absent. */
int tmp117_init(uint8_t addr, int32_t alert_high_mC, int32_t alert_low_mC);
int tmp117_read_mC(uint8_t addr, int32_t *mC);

#endif
