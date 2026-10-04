#ifndef IMPEDANCE_H
#define IMPEDANCE_H

#include <stdint.h>

/* Moisture electrode impedance at 1 kHz, in ohms, from the peak-to-peak swing at the divider midpoint.
 * The board drives a 3.3 V square wave through a 47k reference resistor into the electrode pair:
 *   Z = Rref * swing / (drive - swing).
 * Returns PP_Z_OPEN_OHMS when nothing is connected (dry, lifted, or no pad). */
int32_t impedance_ohms(int32_t swing_uv);

#endif
