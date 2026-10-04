# PulsePatch firmware for the nRF52832 using the nRF Connect SDK (Zephyr).
# NOT BUILT YET. See ../../README.md.
cmake_minimum_required(VERSION 3.20.0)
find_package(Zephyr REQUIRED HINTS $ENV{ZEPHYR_BASE})
project(pulsepatch)

set(CORE ${CMAKE_CURRENT_SOURCE_DIR}/../../core)
target_include_directories(app PRIVATE ${CORE})
target_sources(app PRIVATE
  src/main.c
  ${CORE}/tmp117.c ${CORE}/impedance.c ${CORE}/ph.c ${CORE}/therapy.c ${CORE}/telemetry.c ${CORE}/app.c)
