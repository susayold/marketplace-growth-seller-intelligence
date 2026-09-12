# Power BI Page 1 Premium Repair Plan
## Marketplace Growth & Seller Intelligence — Executive Overview

## 1. Goal

Rebuild **Page 1 only** so it matches the premium MarketLens reference as closely as Power BI allows.

The current draft is functional but still looks like a technical prototype. The repair must improve:

- page geometry;
- visual hierarchy;
- semantic colors;
- KPI cards;
- slicer/header design;
- chart selection;
- insight presentation;
- spacing;
- typography;
- portfolio polish.

Do **not** start Page 2 until Page 1 passes the visual gate.

---

## 2. Source-of-truth

The premium screenshot is a **design reference**, not a numeric source.

Final values must come from the governed analytical release.

### GitHub
https://github.com/susayold/marketplace-growth-seller-intelligence

### Drive analytical release
https://drive.google.com/drive/folders/1OIs5l-txFVY3AOG2VwxOfO2ItCNx3f_5

### Final release bundle
https://drive.google.com/file/d/1zDd53gdqp8Qo7j1KhnD75BfCyJqjJuXr/view?usp=drivesdk

### Project website
https://marketplace-growth-demo-20260912.sangkenny200.chatgpt.site

Existing visible model objects in the current PBIX:

- Category
- CategoryTop5
- ConcentrationStats
- Geo
- Highlights
- Insights
- Monthly
- Pillars
- SellerLifetime
- Snapshot
- StateTop5

Reuse these where valid. Do not create unnecessary duplicates.

---

## 3. Problems visible in the current Page 1

1. Header is clipped and overlapping.
2. The stray `"Historical Oli..."` object should not be in the header.
3. No clean top slicer strip exists.
4. KPI cards are too plain.
5. Active Sellers shows **1,278**, which conflicts with the governed executive headline/default-view expectation of **3,095**.
6. Main trend chart is compressed and hard to read.
7. X-axis dates are overcrowded.
8. Seller concentration visual does not visually behave like a true Lorenz curve.
9. No visible line of equality.
10. No strong Gini summary.
11. Key Insights is a tiny table instead of executive cards.
12. Category labels are raw/technical.
13. Seller-state panel is a bar chart rather than the intended geographic view.
14. Recent Highlights is a tiny table.
15. Several visuals expose scrollbars.
16. Overall alignment and spacing are inconsistent.
17. The page still looks like default Power BI rather than a designed analytics product.

---

# 4. Canvas

Set Page 1 to:

```text
Width: 1920
Height: 1080
Aspect ratio: 16:9
```

Background:

```text
#F4F7FB
```

Use an 8-pixel design grid.

Preferred spacing units:

```text
8 / 16 / 24 / 32 px
```

---

# 5. Semantic color system

Colors must reflect business meaning.

## Marketplace Growth
```text
Blue      #1677FF
Dark Blue #2563EB
Light     #EFF6FF
```

Use for:
- GMV
- orders
- overview
- general marketplace performance

## Acquisition
```text
Purple #7C3AED
Light  #F5F3FF
```

## Activation & Retention
```text
Cyan #06B6D4
Teal #14B8A6
Light #ECFEFF
```

## Healthy Commercial
```text
Green #10B981
Light #ECFDF5
```

## Concentration / Watch
```text
Amber #F59E0B
Light #FFF7ED
```

## Operational Risk
```text
Red #F43F5E
Light #FFF1F2
```

## Typography
```text
Main text  #10213A
Muted text #6B7A90
Border     #E2E8F0
```

---

# 6. Sidebar

Exact target area:

```text
X 0
Y 0
W 230
H 1080
```

Background:

```text
#071C3D
```

Navigation items:

1. Overview
2. Acquisition
3. Activation & Retention
4. Commercial
5. Customer Experience
6. Root Cause
7. Decision Center

Active Overview:

```text
fill #1677FF
text white
icon white
corner radius 12
```

Inactive items:

```text
transparent
text #D3E2F6
icon #AFC7E8
```

At bottom keep a subtle marketplace/cart illustration.

Do not let the illustration overpower the navigation.

Footer:

```text
Last Updated
Sep 12, 2026

Data: Olist Marketplace
Project by Khoi Nguyen
```

---

# 7. Header

Main content begins around:

```text
X = 250
```

Header area:

```text
Y = 20–115
```

Text:

```text
Page 1 of 7

Marketplace Growth & Seller Intelligence

Executive Overview | Turning marketplace data into trusted insights for better decisions
```

Typography:

```text
Page number: 14–16 pt
Title: 28–32 pt bold
Subtitle: 13–15 pt
```

Delete any overlapping objects from the current header.

---

# 8. Header slicers

Place at top-right:

- Date
- Category
- Seller State
- Reset Filters

Style:

```text
white fill
#D8E3F0 border
8–10 px corner radius
```

Create a Reset Filters bookmark.

Default state:

```text
Date = All
Category = All
Seller State = All
```

---

# 9. KPI strip

Position:

```text
Y ≈ 130
H ≈ 145
```

Five equal cards:

1. GMV Proxy
2. Orders
3. Active Sellers
4. Average Order Value
5. Late Delivery Rate

Card style:

```text
rounded corners 16–20 px
subtle semantic-tinted background
semantic icon
soft border
large KPI
small label
small supporting caption
```

Do not use plain white number-only cards.

---

# 10. KPI 1 — GMV Proxy

Theme:

```text
Blue
```

Display:

```text
GMV PROXY
R$13.59M
```

Do not invent growth deltas from the design reference.

If a verified comparison is not available, use:

```text
Full governed extract
```

or:

```text
Executive complete period
```

---

# 11. KPI 2 — Orders

Theme:

```text
Green / teal
```

Display approximately:

```text
ORDERS
98.7K
```

Use the governed measure.

---

# 12. KPI 3 — Active Sellers

Theme:

```text
Purple
```

Current PBIX shows:

```text
1,278
```

This must be audited.

The default All-period governed headline is expected to reconcile to:

```text
3,095
```

Do not hard-code 3,095.

Likely causes to investigate:

- latest-period filter;
- disconnected seller table;
- wrong relationship;
- current visual context;
- measure based on monthly active sellers rather than total observed sellers.

If `SellerLifetime` is one row per seller, test:

```DAX
Active Sellers =
DISTINCTCOUNT ( SellerLifetime[seller_id] )
```

If that metric is static and not date-responsive, rename to:

```text
Total Observed Sellers
```

unless a proper seller-month table is available.

---

# 13. KPI 4 — AOV

Theme:

```text
Amber
```

Measure:

```DAX
AOV =
DIVIDE ( [GMV Proxy], [Orders] )
```

Target display format:

```text
R$137.75
```

---

# 14. KPI 5 — Late Delivery

Theme:

```text
Red
```

Measure:

```DAX
Late Delivery Rate =
DIVIDE (
    SUM ( Monthly[late_orders] ),
    SUM ( Monthly[delivered_orders] )
)
```

Format:

```text
8.1%
```

---

# 15. Main layout

Use this structure:

```text
┌─────────────────────────────────────────────────────────────────┐
│ KPI   KPI   KPI   KPI   KPI                                    │
├──────────────────────────────┬──────────────────┬───────────────┤
│ GMV + Orders Trend           │ Concentration    │ Key Insights  │
│                              │ Lorenz + Gini    │ 4 cards       │
├──────────────┬───────────────┬──────────────────┬───────────────┤
│ Categories   │ States        │ Seller Map       │ Highlights    │
└──────────────┴───────────────┴──────────────────┴───────────────┘
```

---

# 16. Main visual — GMV Proxy & Orders

Approx coordinates:

```text
X 250
Y 300
W 790
H 410
```

Visual:

```text
Line and Clustered Column Chart
```

Columns:

```text
GMV Proxy
```

Line:

```text
Orders
```

Title:

```text
GMV Proxy & Orders Trend (Complete Period Only)
```

X-axis:

```text
MMM YY
```

Examples:

```text
Jan 17
Feb 17
...
Aug 18
```

Do not show long raw date strings.

Executive trends must exclude incomplete tail periods.

---

# 17. Seller concentration panel

Approx coordinates:

```text
X 1060
Y 300
W 540
H 410
```

The current concentration visual must be rebuilt.

The reference requires a **true Lorenz curve**.

Correct logic:

```text
sort sellers by GMV ascending
calculate cumulative seller share
calculate cumulative GMV share
```

A valid Lorenz curve must:

```text
start at 0,0
remain below the equality line
finish at 100%,100%
```

Add:

```text
Line of Equality
```

Also display:

```text
Seller Gini = 0.792
Top 20% seller share = 82.7%
```

---

# 18. Concentration tabs

Create three small button-like tabs:

```text
Lorenz Curve
Top Share
Gini Trend
```

Initially these may be decorative.

Later they can use bookmarks.

Active tab:

```text
Blue fill
white text
```

Inactive:

```text
light gray-blue fill
dark text
```

---

# 19. Key Insights panel

Approx:

```text
X 1620
Y 300
W 280
H 410
```

Remove the current tiny table.

Create four stacked insight cards.

Each:

```text
colored numbered circle
short headline
1–2 lines of explanation
soft tinted background
```

Recommended verified themes:

1. Marketplace scale / trend
2. High seller concentration
3. Operational delivery risk
4. Seller-base scale

Do not use mockup growth numbers unless verified.

---

# 20. Bottom row

Start around:

```text
Y 730
```

Panels:

1. Top 5 Categories
2. Top 5 States
3. Seller Distribution by State
4. Recent Highlights

---

# 21. Top 5 Categories

Approx:

```text
X 250
Y 730
W 350
H 310
```

Use cleaned English category names.

Do not display raw labels like:

```text
bed_bath_table
health_beauty
housewares
```

Use:

```text
Health & Beauty
Electronics
Home & Decor
Sports
Fashion
```

Use actual governed ranking.

Visual:

```text
horizontal bar / data-bar table
```

Columns:

```text
Category
GMV
Share
```

---

# 22. Top 5 States

Approx:

```text
X 620
Y 730
W 350
H 310
```

Columns:

```text
State
GMV
Share
```

Use the governed state ranking.

---

# 23. Seller Distribution by State

Approx:

```text
X 990
Y 730
W 570
H 310
```

Preferred visual:

```text
Brazil Filled Map
Shape Map
or Azure Maps filled-state visual
```

Metric:

```text
Seller Count
```

Tooltip:

```text
State
Seller Count
Seller Share
GMV
GMV Share
```

The current plain state bar chart does not match the reference.

---

# 24. Recent Highlights

Approx:

```text
X 1580
Y 730
W 320
H 310
```

Remove the current tiny text table.

Use stacked signal rows.

Recommended verified metrics:

```text
Seller Gini       0.792
Top 20% Share     82.7%
30D Activation    15.8%
90D Activation    42.1%
Late Review Gap   -1.73
```

These are more defensible than unverified decorative MoM deltas.

---

# 25. Card/container style

Every panel:

```text
white fill
#E2E8F0 border
16–20 px radius
soft shadow
16–22 px internal padding
```

Avoid charts touching their container edge.

---

# 26. Typography

Use one family:

```text
Segoe UI
Aptos
or Inter
```

Suggested hierarchy:

```text
Page title      28–32
Subtitle        13–15
Panel title     16–18
KPI label       11–13
KPI value       28–34
Chart axis       9–11
Insight title   13–15
Insight body    10–12
```

---

# 27. Remove visible scrollbars

The current page shows scrollbars in table visuals.

No scrollbar should appear in the final portfolio screenshot.

Fix by:

- widening the container;
- reducing columns;
- shrinking unnecessary text;
- using data bars;
- removing redundant totals.

---

# 28. Remove default Power BI look

Do not leave:

- default gray visual backgrounds;
- heavy gridlines;
- visual header icons;
- clipped titles;
- raw field names;
- excessive chart borders.

The page must read like a custom analytics product.

---

# 29. Development order

Do not change random objects one at a time.

Use this exact order:

### Pass 1 — Foundation
- set 1920×1080;
- background;
- sidebar;
- alignment guides.

### Pass 2 — Header
- title;
- subtitle;
- slicers;
- reset bookmark.

### Pass 3 — KPI strip
- rebuild all 5 cards;
- fix Active Sellers logic;
- semantic icons/colors.

### Pass 4 — Main row
- trend chart;
- Lorenz + Gini;
- insight cards.

### Pass 5 — Bottom row
- category;
- state;
- map;
- highlights.

### Pass 6 — Interaction
- slicer behavior;
- reset;
- cross-filtering;
- tooltips.

### Pass 7 — Polish
- font sizes;
- borders;
- shadows;
- spacing;
- no scrollbars.

### Pass 8 — QA
- reconcile numbers;
- compare to premium reference;
- export clean screenshot.

---

# 30. Visual QA gate

Do not proceed to Page 2 until all are true:

- [ ] header has no clipping;
- [ ] slicers align cleanly;
- [ ] five KPI cards visually match the premium style;
- [ ] Active Sellers is reconciled;
- [ ] trend chart is readable;
- [ ] incomplete periods are excluded;
- [ ] Lorenz curve is mathematically correct;
- [ ] equality line is shown;
- [ ] Gini 0.792 is visible;
- [ ] Key Insights uses cards, not a table;
- [ ] category names are cleaned;
- [ ] state geographic visual is used;
- [ ] Recent Highlights uses signal rows;
- [ ] no scrollbar appears;
- [ ] visual panels align;
- [ ] final screenshot looks close to the premium reference.

---

# 31. Final screenshot/export procedure

Before screenshot:

1. View → Fit to Page.
2. Collapse Filters pane.
3. Collapse Visualizations pane.
4. Collapse Data pane.
5. Enter Reading View / clean report view if possible.
6. Ensure no visual is selected.
7. Ensure no resize handles are visible.
8. Capture only the report canvas.
9. Export at native 16:9 resolution if available.

---

# 32. Copy-paste prompt for Luna / Power BI AI

```text
Rebuild ONLY Page 1 — Executive Overview of the current Power BI report.

The supplied premium MarketLens screenshot is the visual target.
It is NOT a numeric source.

Use existing governed project tables and metrics.
Do not invent numbers from the screenshot.

PAGE SIZE
1920 × 1080, 16:9.
Background #F4F7FB.

SIDEBAR
230 px wide.
Dark navy #071C3D.
Navigation:
Overview
Acquisition
Activation & Retention
Commercial
Customer Experience
Root Cause
Decision Center

Overview active:
#1677FF fill, white text.

HEADER
Show:
Page 1 of 7
Marketplace Growth & Seller Intelligence
Executive Overview | Turning marketplace data into trusted insights for better decisions

Top-right:
Date slicer
Category slicer
Seller State slicer
Reset Filters button/bookmark.

Remove any clipped/overlapping current title object, including the stray “Historical Oli...” object.

KPI STRIP
Create 5 premium cards:
1 GMV Proxy — blue
2 Orders — green
3 Active Sellers — purple
4 Average Order Value — amber
5 Late Delivery Rate — red

Each card needs:
semantic icon
light semantic fill
large KPI
small label
rounded corners
soft border/shadow

Do not invent growth deltas from the design reference.

Audit Active Sellers:
the current page shows 1,278.
The governed default All-period headline is expected to reconcile to 3,095.
Do not hard-code 3,095.
Fix measure/filter context.

MAIN TREND
Large Line + Clustered Column visual.
Title:
GMV Proxy & Orders Trend (Complete Period Only)
Columns = GMV Proxy
Line = Orders
X-axis = reporting month formatted MMM YY
Exclude incomplete tail periods.

CONCENTRATION
Rebuild as a true Lorenz curve:
sort seller GMV ascending
x = cumulative seller share
y = cumulative GMV share
add line of equality.

Show:
Seller Gini = 0.792
Top 20% seller GMV share = 82.7%

Add visual tabs:
Lorenz Curve
Top Share
Gini Trend

KEY INSIGHTS
Delete the tiny existing table.
Build 4 stacked insight cards with numbered semantic circles and short explanations.

BOTTOM ROW
Top 5 Categories by GMV:
use cleaned English names, GMV and Share.

Top 5 States by GMV:
State, GMV, Share.

Seller Distribution by State:
use a Brazil filled map / shape map / Azure Maps.
Metric = seller count.

Recent Highlights:
replace tiny text table with stacked rows using verified metrics such as:
Seller Gini 0.792
Top 20% share 82.7%
30D activation 15.8%
90D activation 42.1%
Late review gap -1.73

STYLE
Blue   #1677FF
Purple #7C3AED
Cyan   #06B6D4
Green  #10B981
Amber  #F59E0B
Red    #F43F5E

Text #10213A
Muted #6B7A90
Border #E2E8F0

All panels:
white fill
16–20 px rounded corners
soft shadow
16–22 px padding

No:
scrollbars
clipped titles
raw category codes
tiny tables
default gray Power BI styling
unverified mockup values

Do not start Page 2.
Keep iterating Page 1 until it visually resembles the premium reference.
At the end collapse Power BI authoring panes and inspect the clean Fit-to-Page result.
```

---

# 33. Definition of Done

Page 1 is complete only when it looks like a deliberate executive dashboard at first glance, while every displayed number remains traceable to the governed project data.

The correct priority is:

```text
data correctness
+
visual hierarchy
+
semantic color
+
decision-oriented storytelling
```

—not simply placing all required charts on the page.

