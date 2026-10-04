#include "impedance.h"

#include "pp_config.h"

int32_t impedance_ohms(int32_t swing_uv)
{
    int64_t ohms;
    if (swing_uv <= 0) {
        return 0;
    }
    if (swing_uv >= PP_Z_DRIVE_UV - 10000) {
        return PP_Z_OPEN_OHMS;
    }
    ohms = ((int64_t)PP_Z_REF_OHMS * swing_uv) / (PP_Z_DRIVE_UV - swing_uv);
    return ohms > PP_Z_OPEN_OHMS ? PP_Z_OPEN_OHMS : (int32_t)ohms;
}
