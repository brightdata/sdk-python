"""
Tests for column selection in export_csv.

Scraper output is heterogeneous: an optional field is simply absent when a
page does not have it. The column list therefore has to come from every
record, not just the first one, or those values are dropped with no error.
"""

import csv

from brightdata.datasets.utils import export_csv


class TestExportCsvFields:
    def test_fields_missing_from_the_first_record_are_kept(self, tmp_path):
        data = [
            {"url": "a.com", "price": 10},
            {"url": "b.com", "price": 20, "discount": "50%"},
        ]
        filepath = export_csv(data, tmp_path / "out.csv")

        with open(filepath, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            assert reader.fieldnames == ["url", "price", "discount"]
            rows = list(reader)

        assert rows[0]["discount"] == ""
        assert rows[1]["discount"] == "50%"

    def test_column_order_follows_first_appearance(self, tmp_path):
        data = [
            {"b": 1, "a": 2},
            {"c": 3, "a": 4},
            {"d": 5},
        ]
        filepath = export_csv(data, tmp_path / "out.csv")

        with open(filepath, newline="", encoding="utf-8") as f:
            assert next(csv.reader(f)) == ["b", "a", "c", "d"]

    def test_explicit_fields_still_win(self, tmp_path):
        data = [{"url": "a.com", "price": 10}, {"url": "b.com", "discount": "50%"}]
        filepath = export_csv(data, tmp_path / "out.csv", fields=["url"])

        with open(filepath, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            assert reader.fieldnames == ["url"]
            assert [row["url"] for row in reader] == ["a.com", "b.com"]

    def test_matches_what_jsonl_would_have_kept(self, tmp_path):
        # The same result set must not lose keys just because the caller picked
        # CSV over JSONL.
        data = [{"url": "a.com"}, {"url": "b.com", "discount": "50%"}]
        filepath = export_csv(data, tmp_path / "out.csv")

        with open(filepath, newline="", encoding="utf-8") as f:
            columns = set(next(csv.reader(f)))

        assert columns == {key for record in data for key in record}
