# Build this branch on GitHub Actions

This repository includes `.github/workflows/build-ios.yml`. Upload the source to
GitHub, open **Actions → Build Henge iOS (experimental A13/Monterey)**, and run
it with **Run workflow**. Pushes to branches also start a build.

The workflow uses a GitHub-hosted macOS runner and the existing
`ci/build-bitrise.sh` pipeline. It downloads/builds the pinned Husk and StikJIT
dependencies, builds Henge's restore libraries and iOS engine, then packages an
unsigned IPA. On success, download the artifact named
`Henge-A13-Monterey-unsigned`; it contains `Henge.ipa` in a ZIP archive. Install
only after signing/re-signing it with your own supported sideloading method.

## If the workflow fails

Open the failed run and expand the first red step. Common causes are a toolchain
change on the hosted runner, an upstream dependency/build failure, or a project
requirement newer than the runner's selected Xcode. The workflow does not prove
A13 runtime compatibility or Monterey restore/boot support: it only builds the
app package. Those still require testing on the iPhone 11 Pro and an Apple-
accepted restore image.

## Local build

Follow `ios/README.md`. The local build requires macOS, Xcode, xcodegen and the
pinned Husk/StikJIT dependencies. Generated dependencies and build products are
intentionally ignored by Git and recreated by the build scripts.
