#include "fake_hal.h"

#include <string.h>

#include "pp_hal.h"
#include "tmp117.h"

fake_board_t fake;

void fake_set_temp_mC(int which, int32_t mC)
{
    fake.tmp[which].raw = tmp117_mC_to_raw(mC);
}

void fake_reset(void)
{
    memset(&fake, 0, sizeof fake);
    for (int i = 0; i < 3; i++) {
        fake.tmp[i].present = true;
        fake.tmp[i].id = 0x0117;
    }
    fake_set_temp_mC(0, 34250);
    fake_set_temp_mC(1, 32875);
    fake_set_temp_mC(2, 24500);
    fake.moist_swing_uv = 660000;                    /* 11.75 kOhm between the moisture electrodes */
    fake.adc_uv[PP_ADC_PH_DIFF] = 0;                 /* pH 7 */
    fake.adc_uv[PP_ADC_BATTERY] = 1950000;           /* 3.9 V through the 1:2 divider */
    fake.adc_uv[PP_ADC_PAD_ID] = 1055000;            /* about 47k to ground: pad attached */
}

static fake_tmp117_t *tmp_at(uint8_t addr)
{
    if (addr >= 0x48 && addr <= 0x4A && fake.tmp[addr - 0x48].present) {
        return &fake.tmp[addr - 0x48];
    }
    return NULL;
}

int hal_i2c_write(uint8_t addr, const uint8_t *data, size_t len)
{
    fake_tmp117_t *t = tmp_at(addr);
    uint16_t value = len == 3 ? (uint16_t)((data[1] << 8) | data[2]) : 0;
    if (t && len == 3) {
        if (data[0] == 0x01) t->config = value;
        if (data[0] == 0x02) t->high = value;
        if (data[0] == 0x03) t->low = value;
        return 0;
    }
    return -1;
}

int hal_i2c_write_read(uint8_t addr, const uint8_t *wr, size_t wr_len, uint8_t *rd, size_t rd_len)
{
    fake_tmp117_t *t = tmp_at(addr);
    uint16_t value = 0;
    if (wr_len != 1 || rd_len != 2) {
        return -1;
    }
    if (t) {
        switch (wr[0]) {
        case 0x00: value = (uint16_t)t->raw; break;
        case 0x01: value = t->config; break;
        case 0x02: value = t->high; break;
        case 0x03: value = t->low; break;
        case 0x0F: value = t->id; break;
        default: return -1;
        }
    } else {
        return -1;
    }
    rd[0] = (uint8_t)(value >> 8);
    rd[1] = (uint8_t)value;
    return 0;
}

int hal_adc_read_uv(pp_adc_channel_t channel, int32_t *microvolts)
{
    if (fake.adc_fail[channel]) {
        return -1;
    }
    *microvolts = fake.adc_uv[channel];
    return 0;
}

void hal_led_set_permille(uint16_t duty) { fake.led_permille = duty; }

void hal_ultrasound_set(uint16_t amplitude)
{
    if (amplitude && !fake.us_amplitude) {
        fake.us_on_ticks++;
    }
    fake.us_amplitude = amplitude;
}

int hal_moisture_measure_uv(int32_t *swing_uv)
{
    if (fake.moist_fail) {
        return -1;
    }
    *swing_uv = fake.moist_swing_uv;
    return 0;
}

bool hal_temp_alert_active(void) { return fake.alert; }
void hal_status_led(bool on) { fake.status_led = on; }
void hal_delay_ms(uint32_t ms) { fake.now_ms += ms; }

void hal_link_write(const char *line)
{
    fake.lines++;
    strncpy(fake.last_line, line, sizeof fake.last_line - 1);
    if (line[0] == 'R') {
        strncpy(fake.reading_line, line, sizeof fake.reading_line - 1);
    }
}
