/* Hardware abstraction. The core code calls only these; each target (real board, test harness) implements them. */
#ifndef PP_HAL_H
#define PP_HAL_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

typedef enum {
    PP_ADC_PH_DIFF,     /* pH buffer output minus reference electrode */
    PP_ADC_BATTERY,     /* battery through a 1:2 divider */
    PP_ADC_PAD_ID       /* pad ID divider */
} pp_adc_channel_t;

/* All return 0 on success, non-zero on failure. */
int hal_i2c_write(uint8_t addr, const uint8_t *data, size_t len);
int hal_i2c_write_read(uint8_t addr, const uint8_t *wr, size_t wr_len, uint8_t *rd, size_t rd_len);
int hal_adc_read_uv(pp_adc_channel_t channel, int32_t *microvolts);

void hal_led_set_permille(uint16_t duty);   /* 405 nm string, 0 = off, 1000 = full current */
void hal_ultrasound_set(uint16_t amplitude);   /* 0 = off; 1000 = full drive voltage, at the disc's resonance */
/* Drives the moisture electrodes with a 1 kHz square wave and returns the peak-to-peak swing at the
 * divider midpoint, averaged over several cycles. */
int hal_moisture_measure_uv(int32_t *swing_uv);
bool hal_temp_alert_active(void);           /* true when any TMP117 is holding the alert line low */
void hal_status_led(bool on);
void hal_delay_ms(uint32_t ms);
void hal_link_write(const char *line);      /* one text line to the phone or gateway */

#endif
