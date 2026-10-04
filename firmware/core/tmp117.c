#include "tmp117.h"

#include "pp_hal.h"

#define REG_TEMP        0x00
#define REG_CONFIG      0x01
#define REG_HIGH_LIMIT  0x02
#define REG_LOW_LIMIT   0x03
#define REG_DEVICE_ID   0x0F
#define DEVICE_ID       0x0117
/* Continuous conversion, 1 s cycle, 8 averages, thermostat-mode alert, active low. */
#define CONFIG_VALUE    0x0230

/* One count is 7.8125 milli-degrees, which is exactly 125/16. */
int32_t tmp117_raw_to_mC(int16_t raw)
{
    int32_t scaled = (int32_t)raw * 125;
    return (scaled + (scaled >= 0 ? 8 : -8)) / 16;
}

int16_t tmp117_mC_to_raw(int32_t mC)
{
    int32_t scaled = mC * 16;
    return (int16_t)((scaled + (scaled >= 0 ? 62 : -62)) / 125);
}

static int write_reg(uint8_t addr, uint8_t reg, uint16_t value)
{
    uint8_t frame[3] = { reg, (uint8_t)(value >> 8), (uint8_t)value };
    return hal_i2c_write(addr, frame, sizeof frame);
}

static int read_reg(uint8_t addr, uint8_t reg, uint16_t *value)
{
    uint8_t rx[2];
    int err = hal_i2c_write_read(addr, &reg, 1, rx, sizeof rx);
    if (err == 0) {
        *value = (uint16_t)((rx[0] << 8) | rx[1]);
    }
    return err;
}

int tmp117_init(uint8_t addr, int32_t alert_high_mC, int32_t alert_low_mC)
{
    uint16_t id;
    if (read_reg(addr, REG_DEVICE_ID, &id) != 0 || (id & 0x0FFF) != DEVICE_ID) {
        return -1;
    }
    if (write_reg(addr, REG_HIGH_LIMIT, (uint16_t)tmp117_mC_to_raw(alert_high_mC)) != 0 ||
        write_reg(addr, REG_LOW_LIMIT, (uint16_t)tmp117_mC_to_raw(alert_low_mC)) != 0) {
        return -1;
    }
    return write_reg(addr, REG_CONFIG, CONFIG_VALUE);
}

int tmp117_read_mC(uint8_t addr, int32_t *mC)
{
    uint16_t raw;
    int err = read_reg(addr, REG_TEMP, &raw);
    if (err == 0) {
        *mC = tmp117_raw_to_mC((int16_t)raw);
    }
    return err;
}
