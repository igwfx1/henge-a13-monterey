# Henge-A13-Monterey status

This is an experimental source branch, not a tested IPA.

Implemented in this branch:
- A13 device gate for iPhone12,x / iPad12,x identifiers.
- 2 GB default guest RAM on devices with 4 GB physical memory.
- Runtime masking of selected optional guest CPU ID-register fields based on Apple's host feature sysctls.
- A host-conditional SB fallback to DSB SY + ISB; A14+ keeps the original SB instruction when the host reports support.
- Monterey restore metadata inspection and explicit documentation of the signing/boot-ROM blockers.

Not established:
- Successful compilation of the iOS app or static library.
- Successful run on iPhone 11 Pro.
- Full instruction-by-instruction audit of the A13 host ISA.
- Successful Monterey IPSW personalization, restore, or boot.

The branch uses a distinct bundle identifier (`com.henge.a13.monterey`) to avoid replacing a separately installed Henge build when a test IPA is produced.
