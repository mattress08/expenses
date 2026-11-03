---
name: Expenses
description: A private yen ledger where each month is a bank-passbook page.
colors:
  cover: "#1f5a4c"
  cover-deep: "#174438"
  cover-ink: "#eef5f1"
  cover-ink-2: "#bcd3c8"
  page: "#eaf2ec"
  tint: "#dbe8df"
  paper: "#f7faf7"
  fresh: "#ffffff"
  ink: "#17201d"
  ink-2: "#4f5d57"
  rule: "#d3e1d8"
  field: "#9fb7aa"
  seal: "#c43d2b"
  seal-tint: "#f8e3df"
typography:
  figure:
    fontFamily: "BIZ UDPGothic, system-ui, sans-serif"
    fontSize: "56px"
    fontWeight: 700
    lineHeight: 1.05
    letterSpacing: "-0.01em"
    fontFeature: "tnum"
  headline:
    fontFamily: "BIZ UDPGothic, system-ui, sans-serif"
    fontSize: "18px"
    fontWeight: 700
    lineHeight: 1.5
    fontFeature: "tnum"
  body:
    fontFamily: "BIZ UDPGothic, system-ui, sans-serif"
    fontSize: "15px"
    fontWeight: 400
    lineHeight: 1.5
    fontFeature: "tnum"
  label:
    fontFamily: "BIZ UDPGothic, system-ui, sans-serif"
    fontSize: "15px"
    fontWeight: 700
    lineHeight: 1.5
    fontFeature: "tnum"
rounded:
  none: "0px"
spacing:
  rail: "248px"
  gutter: "56px"
  rail-inset: "28px"
  cell: "9px 14px"
  head-cell: "10px 14px"
  section: "48px"
components:
  button-primary:
    backgroundColor: "{colors.cover}"
    textColor: "{colors.fresh}"
    typography: "{typography.label}"
    rounded: "{rounded.none}"
    padding: "8px 18px"
  button-primary-hover:
    backgroundColor: "{colors.cover-deep}"
    textColor: "{colors.fresh}"
  button-text:
    textColor: "{colors.cover}"
    typography: "{typography.body}"
    padding: "4px 6px"
  button-text-danger:
    textColor: "{colors.seal}"
    padding: "4px 6px"
  button-text-danger-hover:
    backgroundColor: "{colors.seal-tint}"
    textColor: "{colors.seal}"
  input:
    backgroundColor: "{colors.fresh}"
    textColor: "{colors.ink}"
    typography: "{typography.body}"
    rounded: "{rounded.none}"
    padding: "7px 9px"
  rail:
    backgroundColor: "{colors.cover}"
    textColor: "{colors.cover-ink}"
    width: "{spacing.rail}"
  rail-item:
    textColor: "{colors.cover-ink}"
    padding: "9px 28px"
  rail-item-active:
    backgroundColor: "{colors.cover-deep}"
    textColor: "{colors.cover-ink}"
    typography: "{typography.label}"
  rail-month-current:
    backgroundColor: "{colors.page}"
    textColor: "{colors.ink}"
    typography: "{typography.label}"
  table-head:
    backgroundColor: "{colors.tint}"
    textColor: "{colors.ink-2}"
    typography: "{typography.label}"
    padding: "{spacing.head-cell}"
  table-row:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink}"
    padding: "{spacing.cell}"
  table-row-hover:
    backgroundColor: "{colors.fresh}"
  table-total:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.fresh}"
    typography: "{typography.label}"
  entry-line:
    backgroundColor: "{colors.fresh}"
    padding: "10px 6px"
---

# Design System: Expenses

## Overview

**Creative North Star: "The Passbook"**

Each month is a page of a bank passbook (通帳). A green cover holds the book together on the left; the page is a pale security tint; purchases print onto near-white paper lines, oldest first, with a running-total column that climbs like a balance. The month closes on its total, printed in reversed ink. Nothing floats, nothing is rounded, and the table columns are the layout grid.

The world is calm and dense, built for entering a batch of card purchases in a row from the keyboard and then reading the month back. Rank comes from weight and from one reversal, never from more sizes. Colour is functional: cover green appears only where something can be done, vermilion only where something is removed. Light only; there is no dark mode.

Motion is a single signature: a newly entered purchase prints across its line column by column, stepped like a printer head, and the month total counts up to its new sum. Both are skipped under reduced motion. There are no rasters, logos, or illustrations, and none should be invented.

**Key Characteristics:**
- Green cover rail on the left, the only moving part; the main area is the page.
- Three type sizes (56 / 18 / 15) in BIZ UDPGothic, tabular figures everywhere.
- Square corners throughout; flat tonal layering, no shadows.
- Tables are the content: tint header, paper rows, 1px rules, reversed ink total row.
- Green means "you can act"; vermilion means "this removes".

## Colors

A green-cast passbook palette: one cover green, a family of green-tinted paper neutrals, a green-black ink, and one vermilion seal.

### Primary
- **Passbook Cover Green** (cover): the rail background, primary buttons, links, text buttons, focus rings, caret, the entry line's top rule, and month-chart bars (which are links). Every place it appears can be clicked or typed into.
- **Deep Cover** (cover-deep): hover for primary buttons and rail items, and the active Ledger/Dashboard item in the rail.
- **Cover Ink** (cover-ink) and **Faded Cover Ink** (cover-ink-2): text on the cover; the faded tone labels the rail's month list heading.

### Secondary
- **Vermilion Seal** (seal): delete actions only, single row or whole month. Its tint (seal-tint) is the hover ground of a delete and the background of an error flash.

### Neutral
- **Security Tint Page** (page): the app ground behind everything outside the rail; also the reversed ground of the current month in the rail.
- **Header Tint** (tint): table header rows and month-nav hover.
- **Printed Paper** (paper): table sheets, chart panel, empty states, flash messages.
- **Fresh Sheet** (fresh): input fields, the entry line, the edit form, row hover, and text on ink and green.
- **Ink** (ink): body text, the reversed total row background, the chart baseline, the current month's bar.
- **Faded Ink** (ink-2): secondary text, table header text, running-total column, notes, share bars on the dashboard.
- **Ruling** (rule): 1px row dividers.
- **Field Line** (field): input borders and the scrollbar thumb.

### Named Rules
**The Act-Or-Remove Rule.** Cover green appears only where something can be done; vermilion only where something is removed. A non-interactive bar or figure is ink or faded ink, never green (the dashboard's share bars are faded ink for this reason).

**The One Reversal Rule.** Ink as a background is reserved for the closing total row of a table. Nothing else is reversed onto ink.

## Typography

**Display Font:** BIZ UDPGothic 700 (with system-ui, sans-serif)
**Body Font:** BIZ UDPGothic 400 (with system-ui, sans-serif)

**Character:** A Japanese universal-design gothic, plain and highly legible, with tabular figures so yen columns align. Self-hosted Latin subset (includes ¥) at 400 and 700. It has no arrow glyphs, so arrows are inline SVG.

### Hierarchy
- **Figure** (700, 56px, 1.05, -0.01em): the one headline number per page, the month or all-time total. Drops to 40px below 820px.
- **Headline** (700, 18px, 1.5): page titles (month name), section headings, the wordmark, the comparison figure.
- **Body** (400, 15px, 1.5): everything else: table cells, meta lines, inputs, buttons.
- **Label** (700, 15px): table headers, primary buttons, active nav, the top classifications in the meta line, total rows.

### Named Rules
**The Three Sizes Rule.** There are exactly three sizes (figure, head, body). New hierarchy is made with weight (400/700), faded ink, or the reversed total row, never a fourth size.

**The Tabular Rule.** All figures use tabular numerals and right-align in their column. Yen is always written `¥1,234`, whole yen.

## Layout

A two-column grid: a fixed 248px cover rail (sticky, full height, scrolls on its own) and a main column with 36px top and 56px side gutters. Page heads put the month name, the 56px figure, and a meta line on the left and the comparison block right-aligned, bottom-aligned on a shared baseline.

Tables are the grid. The ledger uses fixed columns (date 156, name 224, classification 148, amount 104, running total 124, actions 116; notes take the slack) with a 960px minimum and horizontal scroll inside its sheet. Dashboard sections stack with 48px between them; the lower half splits 7fr / 5fr, collapsing to one column below 1100px.

Direction is fixed: older is always up or left, newer down or right. Month lists, charts, and the previous/next nav all run oldest to newest.

Below 820px the rail becomes a top bar (wordmark, Ledger/Dashboard inline, months as a horizontal scroller), main padding drops to 24px 16px, and each ledger row becomes a stacked grid line: date and actions, then name and amount, then classification and running total, then notes. The entry line stacks to two columns with a full-width Print button.

### Named Rules
**The Oldest-First Rule.** Rows print oldest at top, newest at the bottom next to the entry line; the running total climbs down the page and the month's closing balance sits in the Running total column of the total row.

## Elevation & Depth

Flat. No shadows anywhere. Depth is tonal: page tint behind, paper sheets on it, fresh white for anything being written (inputs, the entry line, the edit form, the hovered row). Structure comes from 1px ruling lines, 2px cover-green top rules on writing surfaces, and the 2px ink baseline under the month chart.

### Named Rules
**The Paper-Not-Card Rule.** Surfaces are sheets of paper on the page, not raised cards. Separate them with tone and rules, never shadow or radius.

## Shapes

Square everywhere: zero radius on buttons, inputs, sheets, bars, and the rail. Lines are 1px (row rules, input borders) or 2px (the entry line's green top rule, the chart's ink baseline). Icons are 16px inline SVG strokes (2px, round caps) inheriting text colour.

## Components

### Buttons
Plain, printed, decisive.
- **Shape:** square (0px).
- **Primary:** cover green with white 700 text, 8px 18px padding; used for Print and Save. Hover darkens to deep cover; active nudges down 1px.
- **Text button:** no background, cover-green underlined text (offset 3px), 4px 6px padding.
- **Danger text button:** the same in vermilion; hover fills with seal tint. Its label says exactly what is removed ("Delete all 41 purchases in October 2026"), and it always confirms.
- **Focus:** 2px cover-green outline, 2px offset (cover-ink inside the rail).

### Inputs / Fields
- **Style:** fresh white, 1px field-line border, square, 7px 9px padding, inherits body type.
- **Hover:** border darkens to faded ink.
- **Focus:** border and 1px outline in cover green.
- **Placeholder:** muted green-gray.

### Navigation
- **Rail:** the cover. Wordmark (18px, 700), then Ledger / Dashboard, then the month list, each month showing its total on the right. Items are 9px 28px. Hover is deep cover.
- **Active page item:** weight 700 on deep cover. No side stripe.
- **Current month:** reversed onto the page tint with ink text, as if the page is open at that month.
- **Month nav:** previous / month picker / next, with short month labels beside SVG chevrons; on phones the labels hide and the chevrons stay. Hover is header tint.

### The Printed Page (signature)
The ledger table on a paper sheet: tint header with faded-ink 700 labels, rows of 9px 14px cells on 1px ruling, hover lifts a row to fresh white. Name and classification wrap and are never cut; only notes truncate with an ellipsis and carry the full text in `title`. Row actions (Edit, Delete) are hidden at rest on hover-capable desktops and appear on row hover and focus-within; on touch and narrow screens they are always shown. The table closes on a reversed ink total row with the month's total in the Running total column.

### Entry Line
The last row of the page, where the next purchase prints: fresh white with a 2px cover-green top rule, inline inputs in each column, and a green Print button in the actions column. After printing, the new row draws across column by column (stepped clip, 70ms stagger) and the figure counts up over 700ms with an exponential ease-out; both off under reduced motion.

### Month Chart
Plain CSS bars on a paper panel, 2px apart, on a 2px ink baseline, values above, month labels below. Bars are links, so they are cover green (deep cover on hover); the selected month's bar is ink with a bold value.

## Do's and Don'ts

### Do:
- **Do** use cover green only on things that can be clicked or typed into, and vermilion only for removal.
- **Do** keep to three sizes (56 / 18 / 15) and rank with weight, faded ink, or the reversed total row.
- **Do** use tabular figures and right-align every amount.
- **Do** list rows and months oldest first, older up or left.
- **Do** mark active navigation with weight and deep cover.
- **Do** let names and classifications wrap; truncate only notes, with the full text in `title`.
- **Do** keep every corner square and every surface flat.
- **Do** draw arrows and icons as inline SVG strokes.

### Don't:
- **Don't** add shadows, radius, or raised cards; sheets sit flat on the page.
- **Don't** use green for bars, figures, or decoration that cannot be acted on.
- **Don't** mark the active nav item with a side stripe.
- **Don't** add a fourth type size.
- **Don't** use vermilion for anything that does not remove data.
- **Don't** add a dark mode, logos, or imagery.
