# Hardware note

This repo builds ZMK. ZMK runs on ARM only — nRF52840, RP2040, STM32.

The assembled Worn this config was written for runs **ATmega32U4** (Pro Micro
class), which is 8-bit AVR. Nothing in this repo can be flashed to it.

Measured on the board, 2026-08-29:

| | |
|---|---|
| Running firmware | VID `0xFEED`, product `worn_split`, manufacturer `Trevor Von Seggern` |
| Bootloader | VID `0x2341` PID `0x0037`, `Arduino Micro` by `Arduino LLC` — Caterina |

`0xFEED` is QMK's default vendor ID; ZMK's is `0x1D50`. Neither `worn_split`
nor that manufacturer string appears in any commit of this repo or of
TrevorVonSeggern/zmk-config, so the running firmware was not built here.

`build.yaml` targets `nice_nano@2.0.0/nrf52840/zmk`. Upstream had `pro_micro`,
which is an interconnect rather than a board and fails Zephyr board resolution;
that is why upstream CI has been red since the rename in October 2025. The
nice!nano target builds, and is the right target if the board is ever moved to
that controller — but a green build here is not evidence that the resulting
firmware can run on the current hardware.

To change the keymap on the board as it exists today, use QMK and flash the
`.hex` with avrdude during the ~8 second Caterina window after a reset.
