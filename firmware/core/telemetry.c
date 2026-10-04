#include "telemetry.h"

#include <stdbool.h>

typedef struct {
    char *buf;
    size_t size, len;
} out_t;

static void put(out_t *o, char c)
{
    if (o->len + 1 < o->size) {
        o->buf[o->len] = c;
    }
    o->len++;
}

static void put_u32(out_t *o, uint32_t v)
{
    char digits[10];
    int n = 0;
    do {
        digits[n++] = (char)('0' + v % 10);
        v /= 10;
    } while (v);
    while (n) {
        put(o, digits[--n]);
    }
}

static uint32_t put_sign(out_t *o, int32_t v)
{
    if (v < 0) {
        put(o, '-');
        return 0u - (uint32_t)v;
    }
    return (uint32_t)v;
}

static void put_i32(out_t *o, int32_t v)
{
    put_u32(o, put_sign(o, v));
}

/* Prints a value held in thousandths with three decimals, for example 34250 -> "34.250". */
static void put_milli(out_t *o, int32_t v)
{
    uint32_t u = put_sign(o, v);
    uint32_t frac = u % 1000;
    put_u32(o, u / 1000);
    put(o, '.');
    put(o, (char)('0' + frac / 100));
    put(o, (char)('0' + (frac / 10) % 10));
    put(o, (char)('0' + frac % 10));
}

static size_t finish(out_t *o)
{
    put(o, '\n');
    if (o->size > 0) {
        o->buf[o->len < o->size ? o->len : o->size - 1] = '\0';
    }
    return o->len;
}

size_t telemetry_format_reading(const pp_reading_t *r, char *buf, size_t size)
{
    out_t o = { buf, size, 0 };
    put(&o, 'R');
    put(&o, ',');
    put_u32(&o, r->t_s);
    put(&o, ',');
    put_milli(&o, r->ph_milli);
    put(&o, ',');
    put_milli(&o, r->temp_wound_mC);
    put(&o, ',');
    put_milli(&o, r->impedance_ohm);     /* ohms printed as kilohms */
    put(&o, ',');
    put_milli(&o, r->temp_ref_mC);
    put(&o, ',');
    put_milli(&o, r->temp_ambient_mC);
    put(&o, ',');
    put_i32(&o, r->battery_mV);
    put(&o, ',');
    put_i32(&o, r->pad_id_kohm);
    put(&o, ',');
    for (int shift = 12; shift >= 0; shift -= 4) {
        put(&o, "0123456789ABCDEF"[(r->faults >> shift) & 0xF]);
    }
    return finish(&o);
}

size_t telemetry_format_event(char tag, int32_t a, int32_t b, int32_t c, char *buf, size_t size)
{
    out_t o = { buf, size, 0 };
    put(&o, tag);
    put(&o, ',');
    put_i32(&o, a);
    put(&o, ',');
    put_i32(&o, b);
    put(&o, ',');
    put_i32(&o, c);
    return finish(&o);
}

/* Non-negative decimal with up to three fraction digits, returned in thousandths. Limit 1000.000. */
static bool parse_milli(const char **cursor, uint32_t *out)
{
    const char *p = *cursor;
    uint32_t whole = 0, frac = 0, scale = 100;
    bool any = false;
    while (*p >= '0' && *p <= '9') {
        whole = whole * 10 + (uint32_t)(*p++ - '0');
        any = true;
        if (whole > 1000) {
            return false;
        }
    }
    if (*p == '.') {
        p++;
        while (*p >= '0' && *p <= '9') {
            frac += (uint32_t)(*p++ - '0') * scale;
            scale /= 10;
            any = true;
        }
    }
    if (!any) {
        return false;
    }
    *out = whole * 1000 + frac;
    *cursor = p;
    return true;
}

static bool at_end(const char *p)
{
    while (*p == '\r' || *p == '\n' || *p == ' ') {
        p++;
    }
    return *p == '\0';
}

command_t telemetry_parse(const char *line)
{
    command_t cmd = { CMD_INVALID, 0, 0, 0, 0 };
    uint32_t us_min, us_mw, led_min, led_mw;
    const char *p = line;

    while (*p == ' ') {
        p++;
    }
    if (*p == 'S' && at_end(p + 1)) {
        cmd.type = CMD_STOP;
    } else if (*p == '?' && at_end(p + 1)) {
        cmd.type = CMD_READ;
    } else if (*p == 'T' && p[1] == ',') {
        p += 2;
        if (parse_milli(&p, &us_min) && *p++ == ',' && parse_milli(&p, &us_mw) && *p++ == ',' &&
            parse_milli(&p, &led_min) && *p++ == ',' && parse_milli(&p, &led_mw) && at_end(p)) {
            cmd.type = CMD_THERAPY;
            cmd.us_ms = us_min * 60;          /* thousandths of a minute -> milliseconds */
            cmd.us_uw_cm2 = us_mw * 1000;     /* thousandths of a W -> microwatts */
            cmd.led_ms = led_min * 60;
            cmd.led_uw_cm2 = led_mw;          /* thousandths of a mW -> microwatts */
        }
    }
    return cmd;
}
