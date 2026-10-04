/* Text lines between the patch and the phone or gateway.
 *
 * Patch -> host
 *   R,<uptime_s>,<ph>,<temp_wound_c>,<impedance_kohm>,<temp_ref_c>,<temp_ambient_c>,<battery_mv>,<pad_kohm>,<faults_hex>
 *     ph, temp_wound_c and impedance_kohm are the model's ph, temp_c and impedance_kohm columns
 *   A,<result>,<us_ms>,<led_ms>      answer to a T command (result 0 = started; see therapy_result_t)
 *   E,<reason>,<dose_mj_cm2>,0       session ended (see therapy_end_t); dose is today's light total
 * Host -> patch
 *   T,<us_40khz_min>,<us_40khz_w_cm2>,<led_405nm_min>,<led_405nm_mw_cm2>
 *                                                         start a session (fields from risk_to_dose.session_plan)
 *   S                                                     stop
 *   ?                                                     send a reading now
 */
#ifndef TELEMETRY_H
#define TELEMETRY_H

#include <stddef.h>
#include <stdint.h>

#define PP_FAULT_TEMP_WOUND   0x0001
#define PP_FAULT_TEMP_REF     0x0002
#define PP_FAULT_TEMP_AMBIENT 0x0004
#define PP_FAULT_MOISTURE     0x0008
#define PP_FAULT_PH           0x0010
#define PP_FAULT_BATTERY      0x0020
#define PP_FAULT_PAD          0x0040

typedef struct {
    uint32_t t_s;
    int32_t ph_milli;
    int32_t temp_wound_mC, temp_ref_mC, temp_ambient_mC;
    int32_t impedance_ohm;  /* moisture electrodes at 1 kHz; PP_Z_OPEN_OHMS when nothing is connected */
    int32_t battery_mV;
    int32_t pad_id_kohm;    /* -1 = no pad attached */
    uint16_t faults;
} pp_reading_t;

typedef enum { CMD_INVALID, CMD_THERAPY, CMD_STOP, CMD_READ } cmd_type_t;

typedef struct {
    cmd_type_t type;
    uint32_t us_ms, us_uw_cm2, led_ms, led_uw_cm2;
} command_t;

/* Both write a NUL-terminated line ending in '\n' and return its length (excluding the NUL). */
size_t telemetry_format_reading(const pp_reading_t *r, char *buf, size_t size);
size_t telemetry_format_event(char tag, int32_t a, int32_t b, int32_t c, char *buf, size_t size);
command_t telemetry_parse(const char *line);

#endif
