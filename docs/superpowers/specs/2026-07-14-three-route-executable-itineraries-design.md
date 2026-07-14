# Three-Route Executable Itineraries Design

## Goal

Replace the single detailed itinerary at `/travel/` with three complete,
independently readable itinerary candidates. The page must open in a neutral
comparison state, let the reader choose a route, and then use A/B/C tabs to
switch between the full plans.

The three plans are alternatives, not a recommended route plus two abbreviated
fallbacks. Each plan must include its own dates, flights, transfers, rental-car
plan, lodging, seven-day schedule, food, budget, booking deadlines, fallbacks,
and sources.

## Confirmed Decisions

- Keep the original route set:
  - A: Yining double-wing base route.
  - B: west-to-east continuous route.
  - C: Tangbula deep-stay route.
- Do not mark any route as recommended or select one by default.
- Use a choice-first, high-density layout: show one compact comparison matrix
  before revealing a full itinerary.
- Avoid marketing-style visual design, large cards, decorative spacing, and
  oversized hero copy. Optimize for information density and comparison speed.
- Keep all three plans as static HTML in one page. JavaScript only enhances the
  static content into tabs.
- Give each route a different flight strategy:
  - A optimizes for traveling together.
  - B optimizes for arrival time and independent driver setup.
  - C optimizes for total flight cost and may use Urumqi as the gateway.
- Let each route choose its own seven consecutive days within September
  10-20, 2026.
- Print only the selected itinerary when JavaScript has an active route.
- Preserve the existing unlisted, noindex, read-only, privacy-safe page scope.

## Route Definitions

### Route A: Yining Double-Wing Base / Coordination First

Route A keeps Yining as the stable base. Daxigou is a westward out-and-back
activity, while Tangbula is an eastward two-night stay. The route accepts
backtracking in exchange for simpler lodging, easier weather changes, and fewer
high-risk transfer days.

Flight research must favor keeping all three travelers together while still
providing the required Xi'an business stop of more than six hours. The existing
September 11-17 candidate may remain if refreshed research confirms it is still
the strongest coordination-first week.

Expected lodging pattern:

- Yining base before and after Tangbula.
- Two nights in Tangbula or Bee Town.
- No more than two lodging bases.

Primary trade-off: the safest operational plan has repeated Yining road legs.

### Route B: West-to-East Continuous / Time First

Route B starts in Yining, visits Daxigou, stays near Huocheng or Qingshuihe, then
continues directly across the Ili Valley to Tangbula before returning to Yining.
It minimizes obvious backtracking and feels most like a road trip, but contains
the hardest driving day and more lodging changes.

Flight research must let the two drivers reach Yining early enough to collect
the car and begin ground setup. The non-driving business traveler must route
through Xi'an and reunite in Xinjiang on the same day, with no more than roughly
six hours between arrivals.

Expected lodging pattern:

- Initial Yining night.
- One night near Huocheng or Qingshuihe.
- Two nights in Tangbula or Bee Town.
- Final Yining stay.
- No more than four lodging bases.

Primary trade-off: the Daxigou-to-Tangbula transfer is the trip's longest and
least weather-tolerant driving day.

### Route C: Tangbula Deep Stay / Price First

Route C makes Tangbula the main destination and treats Daxigou as conditional.
It uses a longer Tangbula stay, fewer sightseeing categories, and more
weather-flexible local days.

Flight research must minimize total trip cost rather than airfare alone. It may
use Urumqi as the gateway when the combined airfare plus onward flight, rail, or
road transfer remains materially cheaper than flying into Yining. All transfer
time, transfer cost, and luggage handling must be included in the comparison.
The three travelers must still reunite on the same day without losing a shared
overnight.

Expected lodging pattern:

- Arrival or departure base in Yining.
- Three or more nights in Tangbula or Bee Town.
- Daxigou only when current autumn-color evidence justifies it.

Primary trade-off: the lowest-cost gateway can add transfer complexity and
reduce usable time on the first or final day.

## Neutral High-Density Comparison

The page initially shows:

1. A compact page title, unlisted/noindex warning, research date, and "not
   booked" status line.
2. One dense comparison table with a selectable row for each route.
3. A short trust-label legend and the minimum explanation needed to interpret
   the table.

No route panel is active in the JavaScript-enhanced initial state. The rows
must use equal visual weight and neutral ordering. Route A may appear first for
stable A/B/C naming, but it must not receive a recommendation badge, stronger
color, larger size, or selected state.

Each route row must show:

- Exact seven-day date range.
- Gateway and flight strategy.
- Lodging-base count.
- Longest driving day.
- Number of exceptional-effort days.
- Planning budget for three travelers.
- One-sentence benefit.
- One-sentence real cost.

Selecting a row reveals the matching itinerary and a compact A/B/C tab bar.
The detail view includes a "Back to three-plan comparison" control.

## Information-Density Rules

- Use the existing homepage typefaces and color tokens without adding a new
  visual theme.
- Keep the page wide enough for comparison tables, with a practical desktop
  content width around 1,360-1,440 pixels.
- Prefer flat tables, definition lists, compact timelines, and ruled sections
  over card grids.
- Use small, consistent spacing steps. Do not create large empty hero regions
  or oversized section gaps.
- Keep headings factual and short. Avoid promotional or narrative copy when a
  label, value, or table cell can communicate the same information.
- Put the highest-value fields above the fold: dates, gateway, flight strategy,
  bases, longest drive, budget, benefit, and cost.
- Use route maps and evidence images as secondary reference material, not as
  dominant visual sections.
- Reuse one compact status legend instead of repeating explanatory prose in
  multiple decorative panels.
- Dense does not mean unreadable: table headers, row labels, keyboard focus,
  touch targets, and text contrast must remain accessible.

## Full Route Panel Contract

Every route panel must contain the same section sequence:

1. Route status and research date.
2. Candidate outbound and return flights.
3. Airport, rail, or road transfer plan.
4. Rental-car pickup, driver, insurance, and return plan.
5. Route-specific map and road-distance notes.
6. Seven dated day articles with times, meals, driving, effort, and fallback.
7. Primary and fallback lodging.
8. Route-specific food plan.
9. Itemized ground and all-in budget.
10. Booking deadlines and cancellation requirements.
11. Weather, road, inventory, and fatigue fallbacks.
12. Route-specific sources and verification labels.

IDs must be namespaced by route, for example:

- `route-a-panel`
- `route-a-flight-title`
- `route-a-day-1`
- `route-b-budget-title`

Shared page metadata, privacy warnings, theme controls, and attribution can
remain outside the route panels. Operational travel information must not rely
on content from another panel.

## Interaction Model

### Static Baseline

All three route panels exist in the delivered HTML. Without JavaScript:

- All route details remain visible.
- Comparison rows contain ordinary links to the matching panel IDs.
- There is no hidden itinerary content.
- The page remains readable, navigable, and printable.

### JavaScript Enhancement

After successful initialization:

- The initial state shows the comparison and hides all full panels.
- Selecting a route activates exactly one panel.
- The URL hash becomes `#route-a`, `#route-b`, or `#route-c`.
- Loading a valid route hash opens that route directly.
- Loading an invalid or absent hash returns to the neutral comparison.
- The compact tab bar follows the WAI-ARIA tabs pattern.
- Arrow Left/Right changes tabs.
- Home/End moves to the first/last tab.
- Focus remains visible and predictable.
- Selecting "Back to comparison" clears the route hash and returns focus to the
  chooser heading.

The theme-storage and image-failure initializers remain independent of route
selection. A route-selection failure must not hide static itinerary content.

## Responsive Behavior

- Desktop uses the dense comparison table and compact split layouts where they
  improve scan speed.
- On mobile, the comparison table remains horizontally scrollable inside its
  own wrapper with the route-name column kept easy to identify.
- Route detail sections collapse only where necessary; spacing remains compact.
- The compact route tab bar can scroll horizontally on narrow screens.
- Flight and budget tables scroll inside their own wrappers on screen.
- No route may create page-level horizontal overflow.
- Switching routes must not cause large layout jumps above the tab bar.

## Print Behavior

With JavaScript and an active route:

- Print only the selected route and the shared privacy/status context.
- Hide choice controls, tab controls, theme controls, and navigation.
- Force light, ink-safe theme tokens regardless of explicit or OS dark mode.
- Show all flight-table columns without clipping.
- Keep day blocks intact where possible.
- Use light route/evidence images.

With JavaScript and no active route:

- Print the three route summaries and comparison table only.

Without JavaScript:

- Print all three complete routes because no active route state exists.
- Clearly separate routes with page breaks and route headings.

## Travel Research Rules

Research is part of implementation because the three plans require independent
dates and transport.

For each route:

- Evaluate seven-day windows fully contained within September 10-20, 2026.
- Verify recurring schedules and label them with the research date.
- Do not describe recurring schedules as confirmed exact-date inventory.
- Keep the Xi'an business stop longer than six hours.
- Preserve same-day reunion and the roughly six-hour arrival-gap boundary.
- Include Urumqi-to-Yining transfer cost and time in Route C.
- Include refundable lodging requirements and route-specific cancellation
  deadlines.
- Keep overnight elevations below roughly 2,200 meters.
- Use at most two exceptional-effort days.
- Exclude guide-dependent, unmarked, high-altitude, and routine night-driving
  activities.
- Include at least one lighter meal daily.

Use the existing trust labels:

- `班表已核对`
- `候选`
- `价格待确认`
- `条件项`
- `下单前复核`

Exact fares, room rates, and vehicle prices must remain planning ranges unless
an exact-date public source can be verified.

## Privacy and Publishing

The page remains available to anyone with the URL and must visibly say so. It
must not expose:

- Traveler names.
- Identity or license details.
- Phone numbers.
- Booking references.
- Payment data.
- Room numbers.
- Business counterpart details.
- Exact meeting location.

Keep `noindex`, omit the page from homepage navigation, and preserve safe
external-link attributes.

The social-preview copy must describe three itinerary alternatives rather than
a single final plan. Any changed OG asset must receive a new cache-busting URL.

## Testing

### Static Contract Tests

Tests must prove:

- Three selectable comparison rows exist with equal semantic status.
- Three complete static route panels exist.
- Each panel contains flights, transfer, car, lodging, seven days, food,
  budget, booking deadlines, fallbacks, and sources.
- Dates and IDs are route-specific and unique.
- No route panel depends on another panel for operational information.
- Privacy and noindex rules remain intact.
- CSS, JavaScript, and OG cache versions match the changed assets.

### Script Tests

Tests must prove:

- Missing JavaScript leaves every panel readable.
- Neutral initialization does not select Route A.
- Valid hashes activate the matching route.
- Invalid hashes return to comparison.
- Only one enhanced panel is active.
- Tab keyboard behavior and focus management follow the design.
- Returning to comparison clears route state.

### Style and Browser Tests

Check:

- Desktop comparison and all three route panels.
- Mobile comparison, horizontal tab scrolling, and zero page overflow.
- Explicit light, explicit dark, and OS-auto dark modes.
- Print from comparison, each selected route, explicit dark, and OS dark.
- JavaScript-disabled screen and print output.
- Direct route hashes.

### Deployment Verification

After deployment, verify:

- Public HTML includes all three route summaries and static panels.
- `#route-a`, `#route-b`, and `#route-c` open the correct plans.
- Changed CSS, JavaScript, and OG assets use fresh cache-busting versions.
- The local container and public site serve byte-consistent content.

## Acceptance Criteria

The redesign is complete when:

- A reader first sees a neutral three-plan choice.
- Each choice opens a complete, independently actionable seven-day itinerary.
- The three plans use distinct flight strategies and independently optimized
  dates.
- A/B/C tabs switch reliably without making content JavaScript-dependent.
- Direct links open a specific plan.
- Mobile, dark mode, no-JavaScript, and print behaviors match this design.
- Only the selected route prints in the enhanced state.
- All travel content remains explicitly unbooked and privacy-safe.
- The live `/travel/` deployment serves the new three-plan version and fresh
  assets.
