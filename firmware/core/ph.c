#include "ph.h"

int32_t ph_from_uv(const ph_cal_t *cal, int32_t uv)
{
    int64_t milli;
    if (cal->uv_per_ph == 0) {
        return 7000;
    }
    milli = 7000 + ((int64_t)(uv - cal->uv_at_ph7) * 1000) / cal->uv_per_ph;
    if (milli < 0) {
        return 0;
    }
    if (milli > 14000) {
        return 14000;
    }
    return (int32_t)milli;
}
