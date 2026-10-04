/* PulsePatch on the nRF52832 with the nRF Connect SDK (Zephyr).
 *
 * NOT BUILT OR RUN YET. This file implements pp_hal.h with Zephyr drivers and runs the same core
 * that the host tests exercise. It was written from the documented APIs without the SDK installed,
 * so expect to fix small things on the first build.
 */
#include <string.h>

#include <zephyr/bluetooth/bluetooth.h>
#include <zephyr/device.h>
#include <zephyr/drivers/adc.h>
#include <zephyr/drivers/gpio.h>
#include <zephyr/drivers/i2c.h>
#include <zephyr/drivers/pwm.h>
#include <zephyr/kernel.h>
#include <zephyr/sys/printk.h>
#include <zephyr/sys/util.h>

#include <bluetooth/services/nus.h>

#include "app.h"
#include "pp_hal.h"

#define USER DT_PATH(zephyr_user)
#define US_PERIOD_NS 33333u                  /* 30 kHz: tune to the disc's loaded resonance */
#define LED_PERIOD_US 1000u
#define LEVEL_PERIOD_US 1000u
#define MOISTURE_CYCLES 16

static const struct device *const i2c = DEVICE_DT_GET(DT_NODELABEL(i2c0));
static const struct adc_dt_spec adc[] = {
	ADC_DT_SPEC_GET_BY_IDX(USER, 0), ADC_DT_SPEC_GET_BY_IDX(USER, 1), ADC_DT_SPEC_GET_BY_IDX(USER, 2),
	ADC_DT_SPEC_GET_BY_IDX(USER, 3),          /* moisture divider midpoint; not a pp_adc_channel_t */
};
#define ADC_MOISTURE 3
static const struct pwm_dt_spec led_pwm = PWM_DT_SPEC_GET_BY_NAME(USER, led);
static const struct pwm_dt_spec us_a = PWM_DT_SPEC_GET_BY_NAME(USER, us_a);
static const struct pwm_dt_spec us_b = PWM_DT_SPEC_GET_BY_NAME(USER, us_b);
static const struct pwm_dt_spec us_level = PWM_DT_SPEC_GET_BY_NAME(USER, us_level);
static const struct gpio_dt_spec moist_drv = GPIO_DT_SPEC_GET(USER, moist_drv_gpios);
static const struct gpio_dt_spec us_en = GPIO_DT_SPEC_GET(USER, us_en_gpios);
static const struct gpio_dt_spec alert = GPIO_DT_SPEC_GET(USER, alert_gpios);
static const struct gpio_dt_spec button = GPIO_DT_SPEC_GET(USER, button_gpios);
static const struct gpio_dt_spec status = GPIO_DT_SPEC_GET(USER, status_gpios);

K_MSGQ_DEFINE(command_queue, 64, 4, 1);      /* text lines received over Bluetooth */
static app_t app;

/* ---- pp_hal.h ---- */

int hal_i2c_write(uint8_t addr, const uint8_t *data, size_t len)
{
	return i2c_write(i2c, data, len, addr);
}

int hal_i2c_write_read(uint8_t addr, const uint8_t *wr, size_t wr_len, uint8_t *rd, size_t rd_len)
{
	return i2c_write_read(i2c, addr, wr, wr_len, rd, rd_len);
}

static int adc_read_uv(int channel, int32_t *microvolts)
{
	int16_t raw = 0;
	int32_t mv;
	struct adc_sequence seq = { .buffer = &raw, .buffer_size = sizeof(raw) };
	int err = adc_sequence_init_dt(&adc[channel], &seq);

	if (err == 0) {
		err = adc_read(adc[channel].dev, &seq);
	}
	if (err == 0) {
		mv = raw;
		err = adc_raw_to_millivolts_dt(&adc[channel], &mv);
		*microvolts = mv * 1000;
	}
	return err;
}

int hal_adc_read_uv(pp_adc_channel_t channel, int32_t *microvolts)
{
	return adc_read_uv((int)channel, microvolts);
}

int hal_moisture_measure_uv(int32_t *swing_uv)
{
	/* Toggle the drive pin at about 1 kHz and sample the divider midpoint in each half cycle. */
	int64_t sum = 0;
	int32_t high, low;

	for (int i = 0; i < MOISTURE_CYCLES; i++) {
		gpio_pin_set_dt(&moist_drv, 1);
		k_busy_wait(250);
		if (adc_read_uv(ADC_MOISTURE, &high) != 0) {
			gpio_pin_set_dt(&moist_drv, 0);
			return -1;
		}
		k_busy_wait(150);
		gpio_pin_set_dt(&moist_drv, 0);
		k_busy_wait(250);
		if (adc_read_uv(ADC_MOISTURE, &low) != 0) {
			return -1;
		}
		k_busy_wait(150);
		sum += high - low;
	}
	*swing_uv = (int32_t)(sum / MOISTURE_CYCLES);
	return 0;
}

void hal_led_set_permille(uint16_t duty)
{
	pwm_set_dt(&led_pwm, PWM_USEC(LED_PERIOD_US), PWM_USEC((uint32_t)duty * LED_PERIOD_US / 1000u));
}

void hal_ultrasound_set(uint16_t amplitude)
{
	/* Strength: the boost output is about 9.95 V minus 1.515 x the control voltage, so amplitude 1000
	 * (10 V) needs 0 V of control and amplitude 500 (5 V) needs about 3.3 V.
	 * Drive: two complementary 50% square waves on the H-bridge inputs; the enable line powers the boost. */
	uint32_t target_mv = (uint32_t)amplitude * 10u;
	uint32_t control_mv = target_mv >= 9950u ? 0u : (9950u - target_mv) * 1000u / 1515u;
	uint32_t pulse = amplitude ? US_PERIOD_NS / 2 : 0;

	if (control_mv > 3300u) {
		control_mv = 3300u;
	}
	pwm_set_dt(&us_level, PWM_USEC(LEVEL_PERIOD_US), PWM_USEC(control_mv * LEVEL_PERIOD_US / 3300u));
	pwm_set_dt(&us_a, US_PERIOD_NS, pulse);
	pwm_set_dt(&us_b, US_PERIOD_NS, pulse);
	gpio_pin_set_dt(&us_en, amplitude > 0);
}

bool hal_temp_alert_active(void)
{
	return gpio_pin_get_dt(&alert) > 0;
}

void hal_status_led(bool on)
{
	gpio_pin_set_dt(&status, on);
}

void hal_delay_ms(uint32_t ms)
{
	k_msleep(ms);
}

void hal_link_write(const char *line)
{
	printk("%s", line);
	(void)bt_nus_send(NULL, (const uint8_t *)line, strlen(line));
}

/* ---- Bluetooth ---- */

static void nus_received(struct bt_conn *conn, const uint8_t *const data, uint16_t len)
{
	char line[64] = { 0 };

	ARG_UNUSED(conn);
	memcpy(line, data, MIN(len, sizeof(line) - 1));
	(void)k_msgq_put(&command_queue, line, K_NO_WAIT);
}

static struct bt_nus_cb nus_callbacks = { .received = nus_received };

static const struct bt_data adv[] = {
	BT_DATA_BYTES(BT_DATA_FLAGS, (BT_LE_AD_GENERAL | BT_LE_AD_NO_BREDR)),
	BT_DATA(BT_DATA_NAME_COMPLETE, CONFIG_BT_DEVICE_NAME, sizeof(CONFIG_BT_DEVICE_NAME) - 1),
};
static const struct bt_data scan_response[] = {
	BT_DATA_BYTES(BT_DATA_UUID128_ALL, BT_UUID_NUS_VAL),
};

int main(void)
{
	char line[64];
	bool was_pressed = false;

	if (!device_is_ready(i2c)) {
		printk("i2c not ready\n");
		return 0;
	}
	gpio_pin_configure_dt(&us_en, GPIO_OUTPUT_INACTIVE);
	gpio_pin_configure_dt(&status, GPIO_OUTPUT_INACTIVE);
	gpio_pin_configure_dt(&moist_drv, GPIO_OUTPUT_INACTIVE);
	gpio_pin_configure_dt(&alert, GPIO_INPUT);
	gpio_pin_configure_dt(&button, GPIO_INPUT);
	for (size_t i = 0; i < ARRAY_SIZE(adc); i++) {
		adc_channel_setup_dt(&adc[i]);
	}
	if (bt_enable(NULL) == 0 && bt_nus_init(&nus_callbacks) == 0) {
		bt_le_adv_start(BT_LE_ADV_CONN, adv, ARRAY_SIZE(adv), scan_response, ARRAY_SIZE(scan_response));
	}

	app_init(&app, k_uptime_get_32());
	for (;;) {
		bool pressed = gpio_pin_get_dt(&button) > 0;

		while (k_msgq_get(&command_queue, line, K_NO_WAIT) == 0) {
			app_command(&app, k_uptime_get_32(), line);
		}
		if (pressed && !was_pressed) {
			hal_link_write("B,1,0,0\n");     /* the wearer pressed the pain / odour button */
		}
		was_pressed = pressed;
		app_tick(&app, k_uptime_get_32());
		k_msleep(250);
	}
	return 0;
}
