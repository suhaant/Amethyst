# Board packing results

Grid 0.25 mm, edge pull-back 0.5 mm, routing gap {'2-layer': 0.8, '4-layer': 0.4}, piezo keep-out D16 mm, 6 LEDs.
Utilisation = courtyard area / usable area per side, before spares.
Spare slots = extra 2x2 mm I2C sensors (each with 2 caps) that still fit on the top side: first number keeps the board comfortable, second is the hard maximum.

## Sensing only, radio = nRF52832 module MDBT42Q 16x10

| Sensor set | Board | Stackup | Top used | Bottom used | Verdict | Spare slots |
|---|---|---|---|---|---|---|
| A | 25x25 mm | 2-layer | 51% | 13% | packs but too dense to route | 0 / 0 |
| A | 25x25 mm | 4-layer | 51% | 13% | fits, tight | 0 / 7 |
| A | D32 mm (AirTag size) | 2-layer | 39% | 9% | fits, tight | 0 / 7 |
| A | D32 mm (AirTag size) | 4-layer | 39% | 9% | fits, comfortable | 8 / 14 |
| A | D35 mm (Libre 2 size) | 2-layer | 32% | 8% | fits, comfortable | 2 / 12 |
| A | D35 mm (Libre 2 size) | 4-layer | 32% | 8% | fits, comfortable | 15 / 21 |
| A | 30x40 mm | 2-layer | 26% | 6% | fits, comfortable | 10 / 21 |
| A | 30x40 mm | 4-layer | 26% | 6% | fits, comfortable | 26 / 34 |
| A | 40x40 mm | 2-layer | 19% | 5% | fits, comfortable | 23 / 36 |
| A | 40x40 mm | 4-layer | 19% | 5% | fits, comfortable | 46 / 57 |
| B | 25x25 mm | 2-layer | 54% | 13% | does not fit (imu, ph_buffer, temp_ambient) | - |
| B | 25x25 mm | 4-layer | 58% | 13% | fits, tight | 0 / 3 |
| B | D32 mm (AirTag size) | 2-layer | 44% | 9% | fits, tight | 0 / 2 |
| B | D32 mm (AirTag size) | 4-layer | 44% | 9% | fits, comfortable | 4 / 12 |
| B | D35 mm (Libre 2 size) | 2-layer | 37% | 8% | fits, tight | 0 / 9 |
| B | D35 mm (Libre 2 size) | 4-layer | 37% | 8% | fits, comfortable | 11 / 18 |
| B | 30x40 mm | 2-layer | 30% | 6% | fits, comfortable | 6 / 16 |
| B | 30x40 mm | 4-layer | 30% | 6% | fits, comfortable | 23 / 31 |
| B | 40x40 mm | 2-layer | 22% | 5% | fits, comfortable | 19 / 31 |
| B | 40x40 mm | 4-layer | 22% | 5% | fits, comfortable | 42 / 51 |
| C | 25x25 mm | 2-layer | 50% | 22% | does not fit (afe_ad5941) | - |
| C | 25x25 mm | 4-layer | 50% | 22% | does not fit (afe_ad5941) | - |
| C | D32 mm (AirTag size) | 2-layer | 50% | 17% | does not fit (temp_ambient) | - |
| C | D32 mm (AirTag size) | 4-layer | 51% | 17% | fits, tight | 0 / 6 |
| C | D35 mm (Libre 2 size) | 2-layer | 43% | 14% | fits, tight | 0 / 4 |
| C | D35 mm (Libre 2 size) | 4-layer | 43% | 14% | fits, comfortable | 6 / 14 |
| C | 30x40 mm | 2-layer | 34% | 11% | fits, comfortable | 0 / 13 |
| C | 30x40 mm | 4-layer | 34% | 11% | fits, comfortable | 17 / 26 |
| C | 40x40 mm | 2-layer | 26% | 8% | fits, comfortable | 14 / 29 |
| C | 40x40 mm | 4-layer | 26% | 8% | fits, comfortable | 37 / 48 |

## Sensing only, radio = nRF52832 module BC832 7.8x8.8

| Sensor set | Board | Stackup | Top used | Bottom used | Verdict | Spare slots |
|---|---|---|---|---|---|---|
| A | 25x25 mm | 2-layer | 35% | 12% | fits, comfortable | 0 / 5 |
| A | 25x25 mm | 4-layer | 35% | 12% | fits, comfortable | 8 / 12 |
| A | D32 mm (AirTag size) | 2-layer | 26% | 9% | fits, comfortable | 6 / 11 |
| A | D32 mm (AirTag size) | 4-layer | 26% | 9% | fits, comfortable | 17 / 20 |
| A | D35 mm (Libre 2 size) | 2-layer | 22% | 8% | fits, comfortable | 11 / 16 |
| A | D35 mm (Libre 2 size) | 4-layer | 22% | 8% | fits, comfortable | 25 / 27 |
| A | 30x40 mm | 2-layer | 18% | 6% | fits, comfortable | 19 / 25 |
| A | 30x40 mm | 4-layer | 18% | 6% | fits, comfortable | 36 / 41 |
| A | 40x40 mm | 2-layer | 13% | 4% | fits, comfortable | 33 / 39 |
| A | 40x40 mm | 4-layer | 13% | 4% | fits, comfortable | 55 / 60 |
| B | 25x25 mm | 2-layer | 41% | 12% | fits, tight | 0 / 1 |
| B | 25x25 mm | 4-layer | 41% | 12% | fits, comfortable | 4 / 8 |
| B | D32 mm (AirTag size) | 2-layer | 31% | 9% | fits, comfortable | 2 / 8 |
| B | D32 mm (AirTag size) | 4-layer | 31% | 9% | fits, comfortable | 13 / 15 |
| B | D35 mm (Libre 2 size) | 2-layer | 26% | 8% | fits, comfortable | 7 / 13 |
| B | D35 mm (Libre 2 size) | 4-layer | 26% | 8% | fits, comfortable | 21 / 23 |
| B | 30x40 mm | 2-layer | 21% | 6% | fits, comfortable | 15 / 22 |
| B | 30x40 mm | 4-layer | 21% | 6% | fits, comfortable | 32 / 37 |
| B | 40x40 mm | 2-layer | 16% | 4% | fits, comfortable | 29 / 34 |
| B | 40x40 mm | 4-layer | 16% | 4% | fits, comfortable | 51 / 56 |
| C | 25x25 mm | 2-layer | 48% | 21% | does not fit (imu, temp_ambient) | - |
| C | 25x25 mm | 4-layer | 51% | 21% | fits, tight | 0 / 4 |
| C | D32 mm (AirTag size) | 2-layer | 39% | 16% | fits, tight | 0 / 3 |
| C | D32 mm (AirTag size) | 4-layer | 39% | 16% | fits, comfortable | 8 / 13 |
| C | D35 mm (Libre 2 size) | 2-layer | 32% | 13% | fits, comfortable | 2 / 8 |
| C | D35 mm (Libre 2 size) | 4-layer | 32% | 13% | fits, comfortable | 16 / 21 |
| C | 30x40 mm | 2-layer | 26% | 11% | fits, comfortable | 10 / 18 |
| C | 30x40 mm | 4-layer | 26% | 11% | fits, comfortable | 27 / 33 |
| C | 40x40 mm | 2-layer | 19% | 8% | fits, comfortable | 23 / 32 |
| C | 40x40 mm | 4-layer | 19% | 8% | fits, comfortable | 46 / 53 |

## With therapy (LEDs + piezo + drivers), radio = nRF52832 module MDBT42Q 16x10

| Sensor set | Board | Stackup | Top used | Bottom used | Verdict | Spare slots |
|---|---|---|---|---|---|---|
| A | 25x25 mm | 2-layer | 56% | 33% | does not fit (led_array, moisture_cdc, pad_contacts, ph_buffer, swd_charge, temp_ref, temp_wound, us_bridge) | - |
| A | 25x25 mm | 4-layer | 69% | 48% | does not fit (ph_buffer, swd_charge, temp_ref) | - |
| A | D32 mm (AirTag size) | 2-layer | 50% | 29% | does not fit (moisture_cdc, ph_buffer, swd_charge, temp_ref, temp_wound) | - |
| A | D32 mm (AirTag size) | 4-layer | 58% | 32% | fits, tight | 0 / 2 |
| A | D35 mm (Libre 2 size) | 2-layer | 48% | 25% | fits, tight | 0 / 1 |
| A | D35 mm (Libre 2 size) | 4-layer | 48% | 25% | fits, comfortable | 1 / 11 |
| A | 30x40 mm | 2-layer | 39% | 19% | fits, tight | 0 / 10 |
| A | 30x40 mm | 4-layer | 39% | 19% | fits, comfortable | 12 / 23 |
| A | 40x40 mm | 2-layer | 29% | 13% | fits, comfortable | 9 / 25 |
| A | 40x40 mm | 4-layer | 29% | 13% | fits, comfortable | 32 / 45 |
| B | 25x25 mm | 2-layer | 56% | 33% | does not fit (imu, led_array, moisture_cdc, pad_contacts, ph_buffer, swd_charge, temp_ambient, temp_ref, temp_wound, ui, us_bridge) | - |
| B | 25x25 mm | 4-layer | 69% | 48% | does not fit (imu, ph_buffer, swd_charge, temp_ambient, temp_ref, ui) | - |
| B | D32 mm (AirTag size) | 2-layer | 50% | 29% | does not fit (imu, moisture_cdc, ph_buffer, swd_charge, temp_ambient, temp_ref, temp_wound, ui) | - |
| B | D32 mm (AirTag size) | 4-layer | 62% | 32% | does not fit (temp_ambient) | - |
| B | D35 mm (Libre 2 size) | 2-layer | 50% | 25% | does not fit (imu, ph_buffer, temp_ambient) | - |
| B | D35 mm (Libre 2 size) | 4-layer | 52% | 25% | fits, tight | 0 / 7 |
| B | 30x40 mm | 2-layer | 42% | 19% | fits, tight | 0 / 7 |
| B | 30x40 mm | 4-layer | 42% | 19% | fits, comfortable | 8 / 21 |
| B | 40x40 mm | 2-layer | 31% | 13% | fits, comfortable | 5 / 21 |
| B | 40x40 mm | 4-layer | 31% | 13% | fits, comfortable | 28 / 41 |
| C | 25x25 mm | 2-layer | 56% | 33% | does not fit (afe_ad5941, imu, led_array, pad_contacts, ppg, spectral, swd_charge, temp_ambient, temp_ref, temp_wound, ui, us_bridge) | - |
| C | 25x25 mm | 4-layer | 67% | 50% | does not fit (afe_ad5941, imu, ppg, swd_charge, temp_ambient, temp_ref, temp_wound, ui) | - |
| C | D32 mm (AirTag size) | 2-layer | 53% | 29% | does not fit (imu, led_driver, pmic, ppg, spectral, swd_charge, temp_ambient, temp_ref, temp_wound, ui) | - |
| C | D32 mm (AirTag size) | 4-layer | 63% | 42% | does not fit (imu, swd_charge, temp_ambient, ui) | - |
| C | D35 mm (Libre 2 size) | 2-layer | 52% | 32% | does not fit (imu, swd_charge, temp_ambient, ui) | - |
| C | D35 mm (Libre 2 size) | 4-layer | 58% | 32% | fits, tight | 0 / 4 |
| C | 30x40 mm | 2-layer | 47% | 24% | fits, tight | 0 / 3 |
| C | 30x40 mm | 4-layer | 47% | 24% | fits, comfortable | 3 / 16 |
| C | 40x40 mm | 2-layer | 35% | 17% | fits, comfortable | 0 / 18 |
| C | 40x40 mm | 4-layer | 35% | 17% | fits, comfortable | 22 / 35 |

## With therapy (LEDs + piezo + drivers), radio = nRF52832 module BC832 7.8x8.8

| Sensor set | Board | Stackup | Top used | Bottom used | Verdict | Spare slots |
|---|---|---|---|---|---|---|
| A | 25x25 mm | 2-layer | 49% | 33% | does not fit (led_array, moisture_cdc, ph_buffer, swd_charge, temp_ref, temp_wound) | - |
| A | 25x25 mm | 4-layer | 59% | 45% | does not fit (temp_ref) | - |
| A | D32 mm (AirTag size) | 2-layer | 45% | 31% | fits, tight | 0 / 1 |
| A | D32 mm (AirTag size) | 4-layer | 45% | 31% | fits, comfortable | 3 / 8 |
| A | D35 mm (Libre 2 size) | 2-layer | 38% | 24% | fits, tight | 0 / 5 |
| A | D35 mm (Libre 2 size) | 4-layer | 38% | 24% | fits, comfortable | 11 / 16 |
| A | 30x40 mm | 2-layer | 30% | 18% | fits, comfortable | 5 / 16 |
| A | 30x40 mm | 4-layer | 30% | 18% | fits, comfortable | 22 / 29 |
| A | 40x40 mm | 2-layer | 22% | 13% | fits, comfortable | 19 / 30 |
| A | 40x40 mm | 4-layer | 22% | 13% | fits, comfortable | 41 / 48 |
| B | 25x25 mm | 2-layer | 49% | 33% | does not fit (imu, led_array, moisture_cdc, ph_buffer, swd_charge, temp_ambient, temp_ref, temp_wound, ui) | - |
| B | 25x25 mm | 4-layer | 63% | 45% | does not fit (imu, temp_ambient, temp_ref) | - |
| B | D32 mm (AirTag size) | 2-layer | 47% | 31% | does not fit (ph_buffer, temp_ambient) | - |
| B | D32 mm (AirTag size) | 4-layer | 50% | 31% | fits, tight | 0 / 6 |
| B | D35 mm (Libre 2 size) | 2-layer | 42% | 24% | fits, tight | 0 / 2 |
| B | D35 mm (Libre 2 size) | 4-layer | 42% | 24% | fits, comfortable | 7 / 13 |
| B | 30x40 mm | 2-layer | 34% | 18% | fits, comfortable | 1 / 11 |
| B | 30x40 mm | 4-layer | 34% | 18% | fits, comfortable | 18 / 26 |
| B | 40x40 mm | 2-layer | 25% | 13% | fits, comfortable | 15 / 26 |
| B | 40x40 mm | 4-layer | 25% | 13% | fits, comfortable | 37 / 46 |
| C | 25x25 mm | 2-layer | 51% | 33% | does not fit (imu, led_array, led_driver, pmic, ppg, spectral, swd_charge, temp_ambient, temp_ref, temp_wound, ui) | - |
| C | 25x25 mm | 4-layer | 62% | 47% | does not fit (imu, led_driver, ppg, swd_charge, temp_ambient, temp_ref, temp_wound, ui) | - |
| C | D32 mm (AirTag size) | 2-layer | 47% | 35% | does not fit (imu, led_driver, spectral, swd_charge, temp_ambient, temp_ref, temp_wound, ui) | - |
| C | D32 mm (AirTag size) | 4-layer | 57% | 41% | fits, tight | 0 / 0 |
| C | D35 mm (Libre 2 size) | 2-layer | 46% | 32% | does not fit (imu, temp_ambient) | - |
| C | D35 mm (Libre 2 size) | 4-layer | 48% | 32% | fits, comfortable | 1 / 9 |
| C | 30x40 mm | 2-layer | 38% | 24% | fits, tight | 0 / 7 |
| C | 30x40 mm | 4-layer | 38% | 24% | fits, comfortable | 13 / 22 |
| C | 40x40 mm | 2-layer | 29% | 17% | fits, comfortable | 9 / 23 |
| C | 40x40 mm | 4-layer | 29% | 17% | fits, comfortable | 32 / 40 |
