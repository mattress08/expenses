"""One-off: copy expenses from the old Excel sheet into expenses.db.

Usage: .venv/Scripts/python import_xlsx.py "C:/path/to/Monthly Expense.xlsx"

The sheet has one block per month side by side. Each block starts at a header
cell "Expense", followed by Classification, Date, Amount, Notes columns, and ends
at the first empty row.
"""
import sys
from datetime import datetime

import openpyxl

from app import db, parse_form

# September used "Grocery", later months "supermarket", for the same shops.
RENAME = {"grocery": "supermarket"}


def read_sheet(path):
    """Return (rows, errors). Rows are ready to insert; any error means import nothing."""
    ws = openpyxl.load_workbook(path, data_only=True).active
    rows, errors = [], []
    headers = [c for line in ws.iter_rows() for c in line
               if isinstance(c.value, str) and c.value.strip().lower() == "expense"]
    for head in headers:
        for r in range(head.row + 1, ws.max_row + 1):
            name, cls, day, amount, notes = (ws.cell(r, head.column + i).value for i in range(5))
            if name is None and amount is None:
                break
            cls = str(cls or "").strip().lower()
            form = {
                "name": str(name or ""),
                "classification": RENAME.get(cls, cls),
                "date": day.date().isoformat() if isinstance(day, datetime) else str(day or ""),
                # USD purchases were converted with decimals (2814.56); store whole yen
                "amount": str(round(amount)) if isinstance(amount, (int, float)) else str(amount or ""),
                "notes": str(notes or ""),
            }
            row, error = parse_form(form)
            if error:
                errors.append(f"{ws.cell(r, head.column).coordinate}: {error} {form}")
            else:
                rows.append(row)
    return rows, errors


def main(path):
    rows, errors = read_sheet(path)
    if errors:
        sys.exit("Nothing imported, fix these rows first:\n" + "\n".join(errors))
    with db() as conn:
        # shortcut: refuses to run twice instead of de-duplicating, since real duplicates
        # exist (two coin laundry loads on one day); delete expenses.db to re-import.
        if conn.execute("SELECT COUNT(*) FROM expense").fetchone()[0]:
            sys.exit("expenses.db already has expenses; not importing again.")
        conn.executemany(
            "INSERT INTO expense (name, classification, date, amount, notes) VALUES (?, ?, ?, ?, ?)", rows
        )
    print(f"Imported {len(rows)} expenses, total {sum(r[3] for r in rows):,} yen.")  # no ¥: Windows consoles garble it


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
