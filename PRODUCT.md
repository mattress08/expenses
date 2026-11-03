# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

One person: the owner, a university student living in Tokyo who pays in yen with a Citibank card. They log expenses on a laptop in batches every few days or weekly, working through the card company's purchase emails (each email gives a date and an amount in yen). No other users.

## Product Purpose

Replace a hand-kept monthly Excel sheet with a private record of every purchase and a clear view of where the money goes. The goal is awareness, not budgeting: no limits, targets or alerts. Success means entering a batch of purchases is fast, and the owner can see totals and patterns by month, by category and over all time at a glance.

## Positioning

A personal ledger shaped exactly like the owner's own habit: one row per card purchase, five fields (name, classification, date, amount, notes), months as the unit of review. Nothing of a general finance app: no accounts, syncing, budgets or multiple currencies.

## Operating Context

- Purchases come from Citibank emails; the owner types name and classification themselves, since the email lacks them.
- Typical places: Matsuya, Fuji Mart, Tokyu, coin laundry, PASMO/Suica top-ups, Amazon, school cafeteria.
- Review happens per month, mirroring the old sheet's one-block-per-month layout, with an all-time view on the dashboard.
- Runs on the owner's laptop (`python app.py`, 127.0.0.1, no login) and hosted on PythonAnywhere behind a single password login (see DEPLOY.md). Spending data never goes into git.

## Capabilities and Constraints

- Flask + SQLite, server-rendered Jinja templates, no JS framework or build step. Keep it that way.
- Amounts are whole yen; USD purchases are entered as their yen charge with the USD price in notes.
- Classifications are free text, saved lowercase; the current set is food, supermarket, transport, personal, amazon, education, clothes, laundry, phone, store.
- Features: add, edit, delete expense; browse months (list, previous/next, picker); delete a whole month; dashboard per month and all time (totals, comparison to the same days of last month, average per day/month, by classification, biggest purchases, most frequent places).
- Undecided: importing purchases from the Citibank emails (waiting on a sample email).

## Evidence on Hand

Real data: 103 imported expenses, September to November 2026, ¥271,021 (`expenses.db`). No logo, brand assets or imagery exist; none should be invented.

## Product Principles

1. Entering a batch is the main job: the add form is always one step away and keyboard-fast.
2. Numbers are the content: every figure is exact, in yen, and adds up.
3. Months are the unit: whatever the owner looks at, they know which month it is and can move to the next or previous one.
4. Directions agree: older is always left or up, newer right or down (the owner asked for this).
5. Destructive actions say exactly what they remove, and every change (print, edit, delete, delete month) can be undone, newest first, up to the last 50.

## Accessibility & Inclusion

No specific requirement stated. Keyboard use matters because entry is done in batches on a laptop.
