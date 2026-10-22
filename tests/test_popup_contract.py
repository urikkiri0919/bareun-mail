from html.parser import HTMLParser
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
POPUP_PATH = ROOT / "popup.html"


class PopupContractParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.by_id = {}
        self.text_by_id = {}
        self.labels_for = []
        self.stylesheets = []
        self._id_stack = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        element_id = attrs.get("id")
        if element_id:
            self.by_id[element_id] = (tag, attrs)
            self.text_by_id[element_id] = ""
            self._id_stack.append(element_id)
        if tag == "label" and attrs.get("for"):
            self.labels_for.append(attrs["for"])
        if tag == "link" and "stylesheet" in (attrs.get("rel") or "").split():
            self.stylesheets.append(attrs.get("href", ""))

    def handle_endtag(self, tag):
        if self._id_stack:
            self._id_stack.pop()

    def handle_data(self, data):
        for element_id in self._id_stack:
            self.text_by_id[element_id] += data


class PopupContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source = POPUP_PATH.read_text(encoding="utf-8") if POPUP_PATH.exists() else ""
        cls.popup = PopupContractParser()
        cls.popup.feed(source)

    def test_draft_input_is_a_labeled_textarea(self):
        self.assertIn("draft-input", self.popup.by_id)
        tag, _ = self.popup.by_id["draft-input"]
        self.assertEqual("textarea", tag)
        self.assertIn("draft-input", self.popup.labels_for)

    def test_api_status_is_announced(self):
        self.assertIn("connection-status", self.popup.by_id)
        status = self.popup.text_by_id["connection-status"]
        self.assertIn("API", status)
        self.assertIn("연결", status)

    def test_correction_button_is_disabled_before_api_connection(self):
        self.assertIn("correct-button", self.popup.by_id)
        tag, attrs = self.popup.by_id["correct-button"]
        self.assertEqual("button", tag)
        self.assertIn("disabled", attrs)

    def test_result_area_has_no_fabricated_output(self):
        self.assertIn("result-output", self.popup.by_id)
        self.assertEqual("", self.popup.text_by_id["result-output"].strip())

    def test_popup_links_its_stylesheet(self):
        self.assertIn("popup.css", self.popup.stylesheets)


if __name__ == "__main__":
    unittest.main()
