/* A simulated PulsePatch board for tests: fake sensors on a fake I2C bus, fake ADC, recorded outputs. */
#ifndef FAKE_HAL_H
#define FAKE_HAL_H

#include <stdbool.h>
#include <stdint.h>

typedef struct {
    bool present;
    int16_t raw;                 /* temperature result register */
    uint16_t config, high, low;  /* what the firmware wrote */
    uint16_t id;
} fake_tmp117_t;

typedef struct {
    uint32_t now_ms;
    fake_tmp117_t tmp[3];        /* wound, reference, ambient (addresses 0x48..0x4A) */
    int32_t moist_swing_uv;      /* swing at the moisture divider midpoint */
    bool moist_fail;
    int32_t adc_uv[3];
    bool adc_fail[3];
    bool alert;
    uint16_t led_permille;
    uint16_t us_amplitude;
    bool status_led;
    int us_on_ticks;             /* how many times ultrasound was switched on */
    int lines;                   /* link lines sent */
    char last_line[128];
    char reading_line[128];      /* most recent line starting with 'R' */
} fake_board_t;

extern fake_board_t fake;

void fake_reset(void);                       /* healthy board: sensors present, pad on skin, battery 3.9 V */
void fake_set_temp_mC(int which, int32_t mC);

#endif
