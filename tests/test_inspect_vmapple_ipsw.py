import plistlib
import tempfile
import unittest
import zipfile
from pathlib import Path

from tools.inspect_vmapple_ipsw import IPSWError, inspect_ipsw


class InspectIPSWTests(unittest.TestCase):
    def make_ipsw(self, manifest):
        temp = tempfile.TemporaryDirectory()
        path = Path(temp.name) / "fixture.ipsw"
        with zipfile.ZipFile(path, "w") as archive:
            archive.writestr("BuildManifest.plist", plistlib.dumps(manifest))
            archive.writestr("dummy.bin", b"fixture")
        self.addCleanup(temp.cleanup)
        return path

    def test_monterey_vmapple_identity_is_candidate(self):
        path = self.make_ipsw({
            "ProductVersion": "12.6.1",
            "ProductBuildVersion": "21G217",
            "BuildIdentities": [{"Info": {"ProductType": "VirtualMac2,1", "DeviceClass": "VirtualMac2,1"}}],
        })
        result = inspect_ipsw(path)
        self.assertTrue(result["metadata_candidate"])
        self.assertEqual(result["build_version"], "21G217")

    def test_non_monterey_is_not_candidate(self):
        path = self.make_ipsw({
            "ProductVersion": "15.6.1",
            "ProductBuildVersion": "24G90",
            "BuildIdentities": [{"Info": {"ProductType": "VirtualMac2,1"}}],
        })
        self.assertFalse(inspect_ipsw(path)["metadata_candidate"])

    def test_wrong_product_is_not_candidate(self):
        path = self.make_ipsw({
            "ProductVersion": "12.6.1",
            "ProductBuildVersion": "21G217",
            "BuildIdentities": [{"Info": {"ProductType": "MacBookPro18,1"}}],
        })
        self.assertFalse(inspect_ipsw(path)["metadata_candidate"])

    def test_missing_manifest_is_error(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        path = Path(temp.name) / "bad.ipsw"
        with zipfile.ZipFile(path, "w") as archive:
            archive.writestr("not-manifest.txt", "x")
        with self.assertRaises(IPSWError):
            inspect_ipsw(path)


if __name__ == "__main__":
    unittest.main()
