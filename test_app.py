import html
import json
import os
import re
import tempfile
import unittest
from datetime import date, datetime

import openpyxl

from app import app, parse_form


class ExpenseTest(unittest.TestCase):
    def setUp(self):
        fd, self.path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        app.config["DATABASE"] = self.path
        self.client = app.test_client()

    def tearDown(self):
        os.remove(self.path)

    def add(self, **fields):
        data = {"name": "Matsuya", "classification": "Food", "date": "2026-10-02", "amount": "850", "notes": ""}
        return self.client.post("/add", data={**data, **fields})

    def test_parse_form(self):
        good = {"name": "Lunch", "classification": " Food ", "date": "2026-11-03", "amount": "2,459", "notes": ""}
        self.assertEqual(parse_form(good), (("Lunch", "food", "2026-11-03", 2459, ""), None))
        for bad in ({"amount": "abc"}, {"amount": "-1"}, {"amount": "0"}, {"amount": "12.5"},
                    {"amount": "١٢"}, {"date": "11/03/2026"}, {"name": "  "}):
            row, error = parse_form({**good, **bad})
            self.assertIsNone(row, bad)
            self.assertTrue(error)

    def test_month_view_and_totals(self):
        self.add()
        self.add(name="Fuji Mart", classification="supermarket", amount="3,865", notes="<b>x</b>")
        self.add(name="Mom's Touch", date="2026-11-01", amount="105")
        oct_page = self.client.get("/?month=2026-10").get_data(as_text=True)
        self.assertIn("¥4,715", oct_page)  # month total
        self.assertIn("¥3,865", oct_page)  # supermarket total
        self.assertNotIn('title="Mom', oct_page)  # November row stays out of October
        self.assertIn("&lt;b&gt;x&lt;/b&gt;", oct_page)  # notes are escaped
        this_month = date.today().strftime("%Y-%m")
        self.assertIn(f'value="{this_month}"', self.client.get("/?month=garbage").get_data(as_text=True))

    def test_add_redirects_to_its_month_and_delete(self):
        resp = self.add(date="2026-09-02")
        self.assertIn("month=2026-09", resp.headers["Location"])
        self.client.post("/delete/1", data={"month": "2026-09"})
        self.assertIn("Nothing printed on this page yet", self.client.get("/?month=2026-09").get_data(as_text=True))

    def test_dashboard(self):
        self.add(date="2026-09-02", amount="1,000")
        self.add(date="2026-09-20", amount="9,000")  # after day 2: not in the same-days comparison
        self.add(date="2026-10-02", amount="1,500")
        self.add(name="Monitor", classification="amazon", date="2026-10-15", amount="27,091")
        page = self.client.get("/dashboard?month=2026-10").get_data(as_text=True)
        self.assertIn("¥28,591", page)  # October total
        self.assertIn("+186%", page)  # vs September's full ¥10,000
        self.assertIn("¥922", page)  # 28,591 / 31 days
        self.assertNotIn("matsuya", page)  # 1 visit in October: not a regular
        everything = self.client.get("/dashboard?month=all").get_data(as_text=True)
        self.assertIn("matsuya", everything)  # 3 visits overall
        self.assertIn("¥38,591", everything)  # all time
        self.assertEqual(self.client.get("/dashboard?month=2030-01").status_code, 200)  # empty month

    def test_edit(self):
        self.add(date="2026-10-02")
        self.assertIn('value="matsuya"'.replace("m", "M", 1), self.client.get("/edit/1").get_data(as_text=True))
        resp = self.client.post("/edit/1", data={"name": "Sukiya", "classification": "Food", "date": "2026-09-30",
                                                 "amount": "1,200", "notes": "moved"})
        self.assertIn("month=2026-09", resp.headers["Location"])  # follows the expense to its new month
        sep = self.client.get("/?month=2026-09").get_data(as_text=True)
        self.assertIn("Sukiya", sep)
        self.assertIn("¥1,200", sep)
        self.assertNotIn('title="Matsuya"', self.client.get("/?month=2026-10").get_data(as_text=True))
        # bad input: nothing saved, what was typed stays in the form
        page = self.client.post("/edit/1", data={"name": "Typo", "classification": "food", "date": "2026-09-30",
                                                 "amount": "12.5", "notes": ""}).get_data(as_text=True)
        self.assertIn("whole number", page)
        self.assertIn('value="Typo"', page)
        self.assertIn("Sukiya", self.client.get("/?month=2026-09").get_data(as_text=True))
        self.assertEqual(self.client.get("/edit/99").status_code, 404)

    def test_month_navigation_and_delete_month(self):
        self.add(date="2026-09-02")
        self.add(date="2026-09-30")
        self.add(date="2026-10-01")
        page = self.client.get("/?month=2026-01").get_data(as_text=True)
        self.assertIn("month=2025-12", page)  # previous month crosses the year
        self.assertIn("month=2026-02", page)
        self.assertIn('value="2026-01-01"', page)  # add form defaults into the viewed month
        self.assertIn("Sep 2026", page)  # month rail shows months that have expenses
        self.client.post("/delete-month/2026-09")
        self.assertIn("Nothing printed on this page yet", self.client.get("/?month=2026-09").get_data(as_text=True))
        self.assertIn("Matsuya", self.client.get("/?month=2026-10").get_data(as_text=True))  # other month kept
        self.assertEqual(self.client.post("/delete-month/2026-%").status_code, 404)

    def test_dashboard_all_time(self):
        self.add(date="2026-09-02", amount="1,000")
        self.add(name="Monitor", classification="amazon", date="2026-10-15", amount="27,091")
        page = self.client.get("/dashboard?month=all").get_data(as_text=True)
        self.assertIn("¥28,091", page)  # total of every month
        self.assertIn("¥14,046", page)  # 28,091 / 2 months, rounded
        self.assertIn("biggest month, October 2026", page)
        self.assertIn("Monitor", page)
        self.assertEqual(self.client.get("/dashboard?month=all").status_code, 200)
        os.remove(self.path)  # empty database
        self.assertEqual(self.client.get("/dashboard?month=all").status_code, 200)

    def test_ledger_prints_oldest_first_with_running_total(self):
        self.add(name="Late", date="2026-10-20", amount="300")
        resp = self.add(name="Early", date="2026-10-05", amount="1,000")
        self.assertIn("date=2026-10-05", resp.headers["Location"])  # next entry keeps this date
        self.assertTrue(resp.headers["Location"].endswith("#entry"))
        page = self.client.get(resp.headers["Location"]).get_data(as_text=True)
        self.assertLess(page.index("Early"), page.index("Late"))  # passbook order
        self.assertIn('value="2026-10-05"', page)  # entry line carries the last date
        self.assertIn('class="printed"', page)  # the new row gets the print animation
        late_row = page[page.index("Late"):]
        self.assertIn("¥1,300", late_row[:400])  # running total after both rows

    def test_add_error_keeps_typed_values(self):
        resp = self.add(name="Ramen", amount="12.5", date="2026-10-09")
        self.assertEqual(resp.status_code, 400)
        page = resp.get_data(as_text=True)
        self.assertIn("whole number", page)
        self.assertIn('value="Ramen"', page)
        self.assertIn('value="2026-10-09"', page)

    def test_delete_confirm_survives_apostrophes(self):
        self.add(name="Mom's Touch")
        page = self.client.get("/?month=2026-10").get_data(as_text=True)
        confirm = re.search(r"onsubmit='return confirm\((.*?)\)'", page).group(1)
        self.assertNotIn("'", confirm)  # an apostrophe would end the attribute and skip the confirm
        self.assertEqual(json.loads(html.unescape(confirm)), "Delete Mom's Touch (¥850, 2026-10-02)? You can undo this.")

    def test_undo_reverses_each_change_newest_first(self):
        page = lambda m="2026-10": self.client.get(f"/?month={m}").get_data(as_text=True)
        self.add(name="Matsuya")                                     # 1: print
        self.add(name="Fuji Mart", amount="3,865")                   # 2: print
        self.client.post("/edit/2", data={"name": "Tokyu", "classification": "supermarket",
                                          "date": "2026-09-30", "amount": "100", "notes": ""})  # 3: edit, moves month
        self.client.post("/delete/1", data={"month": "2026-10"})    # 4: delete
        self.assertIn("Last change: Deleted Matsuya (¥850, 2026-10-02)", page())

        resp = self.client.post("/undo")                             # undo 4: Matsuya is back, same id
        self.assertIn("month=2026-10", resp.headers["Location"])
        self.assertIn('href="/edit/1"', page())
        self.client.post("/undo")                                    # undo 3: Fuji Mart back in October at its old amount
        self.assertIn("¥3,865", page())
        self.assertNotIn('title="Tokyu"', page("2026-09"))
        self.client.post("/undo")                                    # undo 2: Fuji Mart gone again
        self.assertNotIn('title="Fuji Mart"', page())
        self.client.post("/undo")                                    # undo 1: empty month
        self.assertIn("Nothing printed on this page yet", page())
        self.assertNotIn("Last change:", page())
        self.client.post("/undo")
        self.assertIn("Nothing to undo.", page())

    def test_undo_delete_month_and_depth_cap(self):
        for d in ("2026-09-02", "2026-09-03", "2026-09-04"):
            self.add(date=d)
        self.client.post("/delete-month/2026-09")
        self.assertIn("Last change: Deleted all 3 purchases in September 2026", self.client.get("/").get_data(as_text=True))
        self.client.post("/undo")
        self.assertIn("¥2,550", self.client.get("/?month=2026-09").get_data(as_text=True))  # all three back
        for _ in range(60):
            self.add()
        import sqlite3
        from contextlib import closing
        with closing(sqlite3.connect(self.path)) as conn:
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM undo_log").fetchone()[0], 50)

    def test_import_sheet(self):
        from import_xlsx import read_sheet

        wb = openpyxl.Workbook()
        ws = wb.active
        ws["B3"], ws["J3"] = "Expense", "expense"
        ws.append([None, "PRAIRIELEARN", "Grocery ", datetime(2026, 9, 2), 2814.56, "18 USD"])  # row 4, cols B-F
        ws["J4"], ws["K4"], ws["L4"], ws["M4"] = "matsuya", "food", datetime(2026, 10, 2), 850
        ws["J5"], ws["K5"], ws["L5"], ws["M5"] = "bad", "food", datetime(2026, 10, 3), "abc"
        path = self.path + ".xlsx"
        wb.save(path)
        try:
            rows, errors = read_sheet(path)
        finally:
            os.remove(path)
        self.assertEqual(rows, [("PRAIRIELEARN", "supermarket", "2026-09-02", 2815, "18 USD"),
                                ("matsuya", "food", "2026-10-02", 850, "")])
        self.assertEqual(len(errors), 1)
        self.assertIn("J5", errors[0])


if __name__ == "__main__":
    unittest.main()
