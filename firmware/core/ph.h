#ifndef PH_H
#define PH_H

#include <stdint.h>

typedef struct {
    int32_t uv_at_ph7;   /* electrode voltage (working minus reference) in a pH 7 buffer */
    int32_t uv_per_ph;   /* slope; negative for a polyaniline electrode, ideally -59160 at 25 C */
} ph_cal_t;

/* Returns milli-pH, limited to 0..14000. */
int32_t ph_from_uv(const ph_cal_t *cal, int32_t uv);

#endif
