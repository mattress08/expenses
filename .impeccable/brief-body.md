# Surface brief: ledger and dashboard (whole app)

Scope: every screen of the app: Ledger (`templates/index.html`), Dashboard (`templates/dashboard.html`), Edit (`templates/edit.html`), shared shell (`templates/base.html`, `templates/_monthnav.html`). Mode: Operate.

Audience and task: the owner, on a laptop, enters a batch of card purchases from Citibank emails, then reviews the month and the dashboard. Constraints: server-rendered Flask/Jinja, no JS framework; months are the unit; older is up/left, newer down/right.

Memorable moment: a new purchase prints onto the next line of the month's page and the running total climbs to its new sum.

Unresolved: none.

## Direction contract

THESIS: Each month is a passbook page. Purchases print oldest to newest with a running-total column that climbs like a balance. Refuses the category default of white summary cards over a newest-first table.

OWN-WORLD: Passbook-cover green (#1f5a4c) owns the left rail and every action; pale security-tint page (#eaf2ec) as ground, near-white paper (#f7faf7) for the printed rows, ink #17201d, vermilion seal (#c43d2b) only for removal. BIZ UDPGothic throughout, tabular figures. Three type sizes; rank by weight and one reversed ink total row. Square corners. Raises: centre-rail (month rail is the only moving part), Crouwel grid (table columns are the layout grid), warm app (green only where you can act, vermilion only where you remove), timetable (three sizes, rank by weight and reversal).

STORY: The owner sees which month they are on and what it cost, enters purchases one after another at the bottom line without touching the mouse, and watches each one print and the total climb. The dashboard reads the same pages as figures.

FIRST VIEWPORT: Left 248px green rail: wordmark, Ledger/Dashboard, months oldest at top with totals, current month reversed onto the page tint. Main: month name, month total at 56px, purchase count and top three classifications, comparison to last month at right; below, the printed table (date, name, classification, amount, running total, notes, actions) ending in the entry line with a green Print button.

FORM: Bank passbook (通帳), candidate 3 of 7 on the ordered list; seed:5079412d5e2ce305.

FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance
