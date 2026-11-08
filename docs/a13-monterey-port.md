# Henge-A13-Monterey experimental port

## What this branch changes

- `ios/Henge/Hardware.swift` accepts A13-era identifiers. For the iPhone 11
  family, `hw.machine` is reported as `iPhone12,x`; A14 iPhone 12 models are
  `iPhone13,x`. Older device families remain blocked.
- The default guest RAM becomes 2 GB on devices with 4 GB physical RAM. The
  iPhone 11 Pro has 4 GB, so this avoids the previous 4 GB guest default that
  would leave effectively no headroom for iOS, the emulator, JIT and Metal.
- `core/sysreg.c` reads Apple's `hw.optional.arm.FEAT_*` sysctls once, then
  masks the corresponding optional fields in the virtual `ID_AA64ISAR0_EL1`
  and `ID_AA64ISAR1_EL1` values when the host explicitly reports a feature is
  absent. If a sysctl is unavailable, its state is treated as unknown and the
  previous virtual value is retained; this avoids accidentally hiding features
  on older OS releases merely because a key is missing.
- `core/translate.c` translates the exact `SB` encoding (`0xd50330ff`) into
  `DSB SY; ISB` only when the host sysctl explicitly reports `FEAT_SB` absent.
  Hosts with SB retain the original single-instruction fast path; unknown
  sysctl results also retain the original path rather than guessing.

## Monterey status

The machine implementation is based on the QEMU `vmapple` / `VirtualMac2,1`
layout, whose reference target is macOS 12 (Monterey). That is a promising
starting point, not proof that this Henge restore path boots Monterey.

The installer deliberately does not list a Monterey build yet. The known
historical VirtualMac2,1 Monterey restore images are not currently shown as
signed by Apple's personalization service. A downloaded IPSW or a valid
`BuildManifest.plist` is not enough: idevicerestore needs Apple to personalize
the restore for the machine's ECID. Do not bypass signing or patch Apple's
restore image. Use the metadata preflight only when you have a genuine IPSW:

```sh
python3 tools/inspect_vmapple_ipsw.py /path/to/Monterey.ipsw
```

A positive result means only that the archive contains Monterey metadata and a
VirtualMac2,1 identity. It does not test TSS authorization, AVPBooter
compatibility, restore success, or boot.

The current `BootROM.swift` fetches and hash-checks AVPBooter from Apple's
macOS 14.6.1 restore image. The source establishes that this ROM boots later
macOS releases; it has not been verified here with Monterey. Do not change its
fixed offsets or expected hash without a real IPSW and a reproducible extraction
and hash check.

## What is not established

- The new host-runnable `tests/test_classify_sb.c` verifies SB reaches the barrier class; the full AArch64 fixture is also assembled separately.
- No full iOS IPA build was run in this Linux workspace.
- No iPhone 11 Pro execution, restore, or macOS boot was performed here.
- The A13 host feature sysctl values have not been read from the user's device.
- Not every optional instruction family has been audited. The sysctl masking
  covers the feature fields listed in `core/sysreg.c`; instructions not covered
  by those fields may still need translation if Monterey or another guest
  executes them.
- The Metal renderer and the 2 GB guest configuration have not been validated
  under iPhone 11 Pro memory pressure.

## First on-device test sequence

1. Build and sign this branch for iOS 17+ with JIT enabled. Do not overwrite the
   user's working Henge install; use a separate bundle identifier for testing.
2. Confirm the device log identifies the model as `iPhone12,3` (iPhone 11 Pro)
   and that the installer is enabled.
3. First test the existing known Sequoia 15.6.1 restore path with 2 GB guest
   RAM. Capture the complete `Documents/henge.log` if restore or boot fails.
4. Confirm the app survives memory pressure and that Metal display output works.
5. Only after the A13 Sequoia baseline works, test a genuine Monterey IPSW if
   Apple personalization accepts it. Record restore logs and the first boot
   failure/panic before changing the device model.

## Build constraints

Henge's documented iOS build requires macOS, Xcode 27+, xcodegen, the Husk
build dependencies, and the restore libraries. This source archive is not an
IPA and cannot be compiled into the iOS app on the iPhone itself using the
provided workflow.
