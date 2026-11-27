# Kintoki console-play guide

This project is intended to be played on compatible consoles. It does not
need to run as a desktop game.

## What will be shipped

### PlayStation 1

The first target is a bootable PS1 ISO containing the Kintoki dance showcase.
The PS1 build must be produced from a PS1-compatible executable, not a normal
Windows/macOS executable. PSn00bSDK is the planned open-source PS1 toolchain;
its build tools include the macros needed to produce PS1 executables and CD
images.

### PSP

The later port will ship as PSP homebrew, normally an `EBOOT.PBP` rather than
an ISO. PSPDEV/PSPSDK is the planned toolchain for that build.

## Player preparation

### PS1 preparation

1. Use a PS1 console and a homebrew-capable loader or compatible optical/media
   setup that you already own and understand.
2. Follow the loader’s current documentation for your exact PS1 model and
   hardware. The loader is responsible for starting user-made software; this
   project does not modify console firmware.
3. Copy the released Kintoki ISO to the loader’s supported media or burn it
   only if your hardware and local laws permit that use.
4. Start the loader, select the Kintoki ISO, and launch it.

### PSP preparation

1. Use a PSP that is already configured to run homebrew through a compatible
   setup for its firmware/model.
2. Connect the PSP storage to the computer.
3. Create this folder if it does not exist:

   `PSP/GAME/KINTOKI/`

4. Copy the release file here:

   `PSP/GAME/KINTOKI/EBOOT.PBP`

5. Eject the storage safely, open **Game → Memory Stick** on the PSP, select
   **Kintoki**, and launch it.

## Build and release checks

Before a release is called console-ready:

- The PS1 ISO boots in a compatible emulator and, when available, on test
  hardware.
- The PSP build produces a valid `EBOOT.PBP` and launches from the exact
  `PSP/GAME/KINTOKI/` path.
- The dance loop, camera movement, audio, and exit path work without desktop
  services or network access.
- The package contains only project-owned or properly licensed code, music,
  models, textures, and documentation.
- No commercial PS1/PSP ROM, firmware image, BIOS, keys, or copyrighted game
  dump is redistributed.

## Troubleshooting

- **PS1 ISO does not boot:** verify the PS1 executable and ISO were built by
  the PS1 toolchain, then test the ISO in a compatible emulator before testing
  hardware.
- **PSP does not show Kintoki:** verify capitalization and folder nesting. The
  file must be exactly `PSP/GAME/KINTOKI/EBOOT.PBP`.
- **PSP reports corrupted data:** confirm the release is a homebrew PBP for
  the target PSP setup; do not rename an ISO, ZIP, or desktop executable to
  `EBOOT.PBP`.
- **No compatible loader:** stop and use the loader’s official documentation
  for the exact console model rather than applying an unknown image or
  firmware file.

## Toolchain references

- PS1: [PSn00bSDK](https://github.com/Lameguy64/PSn00bSDK)
- PSP: [PSPDEV](https://pspdev.github.io/)
