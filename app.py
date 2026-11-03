import calendar
import json
import re
import sqlite3
from contextlib import contextmanager
from datetime import date, timedelta
from pathlib import Path

from flask import Flask, abort, flash, redirect, render_template, request, url_for

app = Flask(__name__)
app.config["DATABASE"] = str(Path(__file__).with_name("expenses.db"))
app.config["SECRET_KEY"] = "local-only"  # only signs flash messages; app is meant for localhost
app.jinja_env.filters["yen"] = lambda n: yen(n)
app.jinja_env.filters["month_name"] = lambda m: date.fromisoformat(m + "-01").strftime("%B %Y")
app.jinja_env.filters["short_month"] = lambda m: date.fromisoformat(m + "-01").strftime("%b %Y")  # Oct 2026
app.jinja_env.filters["short_date"] = lambda d: date.fromisoformat(d).strftime("%b ") + str(int(d[8:10]))  # Oct 3

MONTH_RE = r"\d{4}-(0[1-9]|1[0-2])"


@contextmanager
def db():
    """Open a connection, commit on success, always close (sqlite3's own `with` only commits)."""
    conn = sqlite3.connect(app.config["DATABASE"])
    conn.row_factory = sqlite3.Row
    conn.execute(
        """CREATE TABLE IF NOT EXISTS expense (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            classification TEXT NOT NULL,
            date TEXT NOT NULL,
            amount INTEGER NOT NULL,  -- whole yen
            notes TEXT NOT NULL DEFAULT ''
        )"""
    )
    # Undo stack: each change stores the rows as they were before it and the ids that exist after it.
    conn.execute(
        """CREATE TABLE IF NOT EXISTS undo_log (
            id INTEGER PRIMARY KEY,
            label TEXT NOT NULL,
            month TEXT NOT NULL,
            before TEXT NOT NULL,     -- JSON list of full expense rows to put back
            after_ids TEXT NOT NULL   -- JSON list of expense ids to remove
        )"""
    )
    try:
        with conn:
            yield conn
    finally:
        conn.close()


UNDO_DEPTH = 50


def yen(n):
    return f"¥{n:,}"


def log_change(conn, label, month, before, after_ids):
    """Record one change so /undo can reverse it. Keeps the last UNDO_DEPTH changes."""
    conn.execute(
        "INSERT INTO undo_log (label, month, before, after_ids) VALUES (?, ?, ?, ?)",
        (label, month, json.dumps([dict(r) for r in before]), json.dumps(after_ids)),
    )
    conn.execute("DELETE FROM undo_log WHERE id <= (SELECT MAX(id) FROM undo_log) - ?", (UNDO_DEPTH,))


def parse_form(form):
    """Return (row, error). Amount is whole yen; commas like 2,459 are allowed."""
    name = form.get("name", "").strip()
    classification = form.get("classification", "").strip().lower()
    notes = form.get("notes", "").strip()
    if not name or not classification:
        return None, "Name and classification are required."
    try:
        day = date.fromisoformat(form.get("date", "")).isoformat()
    except ValueError:
        return None, "Date must be YYYY-MM-DD."
    amount = form.get("amount", "").replace(",", "").strip()
    if not amount.isascii() or not amount.isdigit() or int(amount) <= 0:
        return None, "Amount must be a whole number of yen above 0."
    return (name, classification, day, int(amount), notes), None


def pick_month(allow_all=False):
    """The ?month=YYYY-MM to show ("all" too if allowed), or the current month if missing or malformed."""
    month = request.args.get("month", "")
    if re.fullmatch(MONTH_RE, month) or (allow_all and month == "all"):
        return month
    return date.today().strftime("%Y-%m")


def shift_month(month, delta):
    y, m = divmod(int(month[:4]) * 12 + int(month[5:]) - 1 + delta, 12)
    return f"{y:04d}-{m + 1:02d}"


app.jinja_env.globals["shift"] = shift_month


def date_pattern(month):
    """LIKE pattern matching ISO dates in `month`, or every date for "all"."""
    return "%" if month == "all" else month + "-%"


def totals_by_class(conn, month):
    return conn.execute(
        "SELECT classification, SUM(amount) AS total, COUNT(*) AS n FROM expense"
        " WHERE date LIKE ? GROUP BY classification ORDER BY total DESC",
        (date_pattern(month),),
    ).fetchall()


def monthly_totals(conn):
    return conn.execute(
        "SELECT substr(date, 1, 7) AS month, SUM(amount) AS total, COUNT(*) AS n FROM expense GROUP BY 1 ORDER BY 1"
    ).fetchall()


def classes(conn):
    return [r[0] for r in conn.execute("SELECT DISTINCT classification FROM expense ORDER BY 1")]


def compare_prev(conn, month, total):
    """Compare `month` with the month before. Mid-month, only the same days of last month count."""
    today = date.today()
    first = date.fromisoformat(month + "-01")
    prev_month = shift_month(month, -1)
    is_current = month == today.strftime("%Y-%m")
    days = today.day if is_current else calendar.monthrange(first.year, first.month)[1]
    prev_total = conn.execute(
        "SELECT COALESCE(SUM(amount), 0) FROM expense WHERE date LIKE ? AND CAST(substr(date, 9, 2) AS INTEGER) <= ?",
        (date_pattern(prev_month), days),
    ).fetchone()[0]
    return dict(
        days=days,
        is_current=is_current,
        prev_month=prev_month,
        prev_total=prev_total,
        change=round(100 * (total - prev_total) / prev_total) if prev_total else None,
    )


@app.context_processor
def rail():
    """Every page shows the month rail (oldest month first) and the latest change that Undo would reverse."""
    with db() as conn:
        return {
            "rail_months": monthly_totals(conn),
            "last_change": conn.execute("SELECT label FROM undo_log ORDER BY id DESC LIMIT 1").fetchone(),
        }


def render_ledger(month, entry=None, status=200):
    today = date.today()
    with db() as conn:
        rows = conn.execute(
            "SELECT * FROM expense WHERE date LIKE ? ORDER BY date, id", (date_pattern(month),)
        ).fetchall()
        by_class = totals_by_class(conn, month)
        class_list = classes(conn)
        total = sum(r["amount"] for r in rows)
        cmp = compare_prev(conn, month, total)
    running, printed = 0, []
    for r in rows:  # the passbook's balance column: what the month has cost up to this row
        running += r["amount"]
        printed.append((r, running))
    if entry is None:
        # batch entry: keep the date of the purchase just printed, else a date inside the month shown
        last = request.args.get("date", "")
        if not (last.startswith(month) and re.fullmatch(r"\d{4}-\d{2}-\d{2}", last)):
            last = today.isoformat() if month == today.strftime("%Y-%m") else month + "-01"
        entry = {"date": last}
    return render_template(
        "index.html",
        rows=printed,
        by_class=by_class,
        classes=class_list,
        total=total,
        cmp=cmp,
        month=month,
        prev_month=shift_month(month, -1),
        next_month=shift_month(month, 1),
        entry=entry,
        printed_id=request.args.get("printed", type=int),
    ), status


@app.get("/")
def index():
    return render_ledger(pick_month())


@app.get("/dashboard")
def dashboard():
    month = pick_month(allow_all=True)
    today = date.today()
    with db() as conn:
        by_class = totals_by_class(conn, month)
        monthly = monthly_totals(conn)
        biggest = conn.execute(
            "SELECT * FROM expense WHERE date LIKE ? ORDER BY amount DESC, date LIMIT 5", (date_pattern(month),)
        ).fetchall()
        places = conn.execute(
            "SELECT lower(trim(name)) AS place, COUNT(*) AS n, SUM(amount) AS total FROM expense"
            " WHERE date LIKE ? GROUP BY 1 HAVING n > 1 ORDER BY n DESC, total DESC LIMIT 8",
            (date_pattern(month),),
        ).fetchall()
        span = conn.execute("SELECT MIN(date), MAX(date) FROM expense").fetchone()

        total = sum(c["total"] for c in by_class)
        stats = dict(total=total, count=sum(c["n"] for c in by_class))
        if month == "all":
            # days from the first expense to today (or the last expense, if dated in the future)
            first = date.fromisoformat(span[0]) if span[0] else today
            last = max(today, date.fromisoformat(span[1])) if span[1] else today
            stats.update(
                days=(last - first).days + 1,
                per_month=round(total / len(monthly)) if monthly else 0,
                top_month=max(monthly, key=lambda m: m["total"], default=None),
            )
        else:
            stats.update(compare_prev(conn, month, total), all_time=sum(m["total"] for m in monthly))
    stats["per_day"] = round(total / stats["days"]) if stats["days"] > 0 else 0

    return render_template(
        "dashboard.html",
        month=month,
        s=stats,
        by_class=by_class,
        class_max=max((c["total"] for c in by_class), default=1),
        monthly=monthly,
        monthly_max=max((m["total"] for m in monthly), default=1),
        biggest=biggest,
        places=places,
    )


@app.post("/add")
def add():
    row, error = parse_form(request.form)
    if error:
        # show the ledger again with what was typed, so a batch entry is not lost
        month = request.form.get("month", "")
        month = month if re.fullmatch(MONTH_RE, month) else date.today().strftime("%Y-%m")
        flash(error, "error")
        return render_ledger(month, entry=request.form, status=400)
    with db() as conn:
        new_id = conn.execute(
            "INSERT INTO expense (name, classification, date, amount, notes) VALUES (?, ?, ?, ?, ?)", row
        ).lastrowid
        log_change(conn, f"Printed {row[0]} ({yen(row[3])})", row[2][:7], [], [new_id])
    return redirect(url_for("index", month=row[2][:7], date=row[2], printed=new_id, _anchor="entry"))


@app.route("/edit/<int:expense_id>", methods=["GET", "POST"])
def edit(expense_id):
    with db() as conn:
        expense = conn.execute("SELECT * FROM expense WHERE id = ?", (expense_id,)).fetchone()
        if expense is None:
            abort(404)
        if request.method == "POST":
            row, error = parse_form(request.form)
            if not error:
                conn.execute(
                    "UPDATE expense SET name = ?, classification = ?, date = ?, amount = ?, notes = ? WHERE id = ?",
                    (*row, expense_id),
                )
                log_change(conn, f"Edited {expense['name']}", expense["date"][:7], [expense], [expense_id])
                return redirect(url_for("index", month=row[2][:7], printed=expense_id))
            flash(error, "error")
            expense = {**expense, **request.form}  # keep what was typed, so a typo is not lost
        class_list = classes(conn)
    return render_template("edit.html", e=expense, classes=class_list, month=expense["date"][:7])


@app.post("/delete/<int:expense_id>")
def delete(expense_id):
    with db() as conn:
        old = conn.execute("SELECT * FROM expense WHERE id = ?", (expense_id,)).fetchone()
        if old is not None:
            conn.execute("DELETE FROM expense WHERE id = ?", (expense_id,))
            log_change(conn, f"Deleted {old['name']} ({yen(old['amount'])}, {old['date']})", old["date"][:7], [old], [])
    return redirect(url_for("index", month=request.form.get("month")))


@app.post("/delete-month/<month>")
def delete_month(month):
    if not re.fullmatch(MONTH_RE, month):
        abort(404)
    with db() as conn:
        old = conn.execute("SELECT * FROM expense WHERE date LIKE ?", (date_pattern(month),)).fetchall()
        conn.execute("DELETE FROM expense WHERE date LIKE ?", (date_pattern(month),))
        if old:
            name = date.fromisoformat(month + "-01").strftime("%B %Y")
            log_change(conn, f"Deleted all {len(old)} purchases in {name}", month, old, [])
    flash(f"Deleted {len(old)} expenses from {month}.", "info")
    return redirect(url_for("index", month=month))


@app.post("/undo")
def undo():
    """Reverse the latest logged change. Pressing again steps further back."""
    with db() as conn:
        last = conn.execute("SELECT * FROM undo_log ORDER BY id DESC LIMIT 1").fetchone()
        if last is None:
            flash("Nothing to undo.", "info")
            return redirect(url_for("index"))
        conn.executemany("DELETE FROM expense WHERE id = ?", [(i,) for i in json.loads(last["after_ids"])])
        # plain INSERT, not REPLACE: an id clash means the log is out of step, so fail and roll back
        conn.executemany(
            "INSERT INTO expense (id, name, classification, date, amount, notes)"
            " VALUES (:id, :name, :classification, :date, :amount, :notes)",
            json.loads(last["before"]),
        )
        conn.execute("DELETE FROM undo_log WHERE id = ?", (last["id"],))
    flash(f"Undone: {last['label']}.", "info")
    return redirect(url_for("index", month=last["month"]))


if __name__ == "__main__":
    app.run(debug=True)  # binds 127.0.0.1 only
