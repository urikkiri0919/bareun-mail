import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "manifest.json"


def load_manifest():
    if not MANIFEST_PATH.exists():
        return {}
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


class ManifestContractTests(unittest.TestCase):
    def test_manifest_uses_v3_and_declares_popup(self):
        manifest = load_manifest()
        self.assertEqual(3, manifest.get("manifest_version"))
        self.assertEqual("popup.html", manifest.get("action", {}).get("default_popup"))

    def test_default_action_shortcut_is_ctrl_shift_e(self):
        manifest = load_manifest()
        command = manifest.get("commands", {}).get("_execute_action", {})
        self.assertEqual("Ctrl+Shift+E", command.get("suggested_key", {}).get("default"))

    def test_extension_requests_no_permissions(self):
        manifest = load_manifest()
        self.assertFalse(manifest.get("permissions", []))
        self.assertFalse(manifest.get("host_permissions", []))


if __name__ == "__main__":
    unittest.main()
