# Monterey guest support status

## What the current code already provides

Henge's virtual machine is based on Apple's `VirtualMac2,1` / QEMU `vmapple`
layout. The source comment in `devices/vmapple.c` explicitly identifies the
QEMU reference implementation as targeting macOS 12 (Monterey) guests. The
base machine includes the core devices used by that model: GICv3, PL011, PL031,
GPIO, PCIe, AES, virtio block/network/input/sound and the virtual USB restore
port. This makes Monterey a technically reasonable guest target to investigate;
it does not prove that a particular Monterey restore image will boot.

The current installer does not hard-code a minimum guest macOS version in the
restore call. `ios/Henge/Installer.swift` passes the selected IPSW path to
`henge_vm_install`, and `host/install.c` passes that path to the vendored
`idevicerestore` implementation. The current picker only offers newer builds.

Henge obtains its AVPBooter from Apple's macOS 14.6.1 restore image in
`ios/Henge/BootROM.swift`. The ROM is hash-checked before use. The source says
this ROM boots later releases; it has not been verified here against Monterey.

## Why this patch does not add Monterey to the normal picker

The historical Monterey `VirtualMac2,1` restore image commonly referenced is
`UniversalMac_12.6_21G115_Restore.ipsw`. The existing restore path asks Apple's
restore/personalization service to authorize firmware for the machine ECID.
An IPSW being downloadable or having a valid BuildManifest is not proof that
Apple will still personalize it. No signing result or successful Monterey
restore was available in this workspace, so adding it as a normal one-tap
installer would misrepresent its status.

Do not bypass Apple's signing/personalization or patch the restore image. If a
Monterey IPSW is available, first inspect its metadata with:

```sh
python3 tools/inspect_vmapple_ipsw.py /path/to/UniversalMac_Monterey_Restore.ipsw
```

The tool verifies ZIP integrity and checks `BuildManifest.plist` for macOS 12
and a `VirtualMac2,1` identity. It is only a metadata preflight: it cannot check
Apple TSS signing, restore authorization, firmware compatibility, or boot.

## Remaining work to establish real support

1. Obtain a genuine Monterey `VirtualMac2,1` restore image and verify that
   Apple's restore service still personalizes it for a fresh ECID.
2. Run the restore on an already-supported host/device before changing the
   CPU compatibility work. Capture the complete `HV_INSTALL_LOG=1` output.
3. If restore succeeds, boot the installed disk and capture the first panic or
   boot failure. Compare the device-tree/MMIO accesses against the Monterey
   guest drivers; do not remove later devices speculatively.
4. Verify the AVPBooter extracted by the current `BootROM.swift` against that
   Monterey restore path. If it is rejected, investigate a compatible Apple
   boot ROM source without modifying Apple's signed firmware.
5. Only after a successful Monterey boot should a Monterey-specific device or
   CPU profile be introduced. Keep the default Sequoia profile unchanged.

## Scope of this change

This patch adds a local IPSW metadata inspector and fixture tests. It does not
claim Monterey runtime support and deliberately does not add an unverified
Monterey download URL to the installer picker.
