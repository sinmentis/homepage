# Three-Route Executable Itineraries Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the single `/travel/` itinerary with a neutral, high-density comparison and three independently actionable seven-day itineraries selected through accessible A/B/C tabs.

**Architecture:** Keep all route content in static HTML so it remains readable without JavaScript. JavaScript progressively enhances the comparison links into hash-addressable tabs, while CSS provides a dense table-first layout and selected-route print behavior. Use the validated research reports as the content source and preserve the existing static-site, Python `unittest`, Podman, nginx, and user-systemd deployment.

**Tech Stack:** Static HTML, scoped CSS, vanilla JavaScript, Python `unittest`, SVG/PNG assets, Playwright for manual browser inspection, Podman, nginx, user systemd.

## Global Constraints

- Work only in `/home/shunlyu/work/website/homepage-travel-itinerary`, except
  for the explicitly required update to
  `/home/shunlyu/work/private/travel_plan/CONTEXT.md`.
- Do not modify `/home/shunlyu/work/website/homepage/.gitignore` or discard its existing user change.
- Do not add dependencies.
- Use Simplified Chinese for public travel content and English for source code, tests, comments, commits, and documentation.
- Keep `/travel/` absent from homepage navigation and retain `<meta name="robots" content="noindex, nofollow">`.
- Do not publish traveler names, identity details, phone numbers, booking references, payment data, room numbers, business counterpart details, or an exact meeting location.
- Do not mark any route as recommended or preselect a route.
- Use a high-density, utilitarian layout: compact tables, definition lists, and timelines; no large marketing hero, decorative cards, gradients, decorative shadows, or oversized whitespace.
- Keep all three route panels in static HTML. Route selection must remain a progressive enhancement.
- Route A: September 12-18, 2026, Yining double-wing base, coordination first, CNY 26,300-46,900.
- Route B: shared Xinjiang trip September 12-18, 2026; business traveler starts September 11 evening; west-to-east continuous route, time first, CNY 25,150-30,300.
- Route C: September 10-16, 2026, Tangbula deep stay, Urumqi price-first gateway, CNY 24,862-40,772.
- Use `研究更新时间：2026-07-14` and retain `班表已核对`, `候选`, `价格待确认`, `条件项`, and `下单前复核`.
- Treat GS7607/GS7608 as Tue/Thu/Sat, XIY 12:10→YIN 16:25 and YIN 17:10→XIY 20:50.
- Do not publish 3U5039/3U5040 exact times as verified. Describe daily XIY↔YIN service as a candidate corridor with exact flight and time checked before booking.
- Route A must show `6 小时 14 分计划间隔 / 约 5–5.5 小时可用时间` and make an Xi'an overnight the safer default.
- Route B must show beside its date that the business traveler personally travels September 11 evening through September 18 while the shared Xinjiang trip remains seven days and six nights.
- Route B must publish the conservative Qingshuihe/Bee Town transfer as `约 300–360 公里 / 4–7 小时` pending Amap/Baidu verification.
- Route B must exclude horse-riding ascent and any Fairy Lake/high-altitude hike extension.
- Route C's driver-pair Urumqi flight must depart no earlier than 16:30 after C848 reaches Urumqi at 14:08/14:17.
- Route C must present CZ6853 as the preferred Xi'an-stop candidate only with a `下单前复核` warning that a technical stop is unconfirmed.
- Print selected route only when enhanced; print summaries when enhanced without a route; print all routes without JavaScript.
- Bump each asset only in the task that changes it: CSS `v=7` in the CSS task,
  JavaScript `v=5` in the JavaScript task, and OG image `v=4` in the preview task.

## Authoritative Content Inputs

- Design: `docs/superpowers/specs/2026-07-14-three-route-executable-itineraries-design.md`
- Route A research: `.superpowers/research/route-a.md`
- Route B research: `.superpowers/research/route-b.md`
- Route C research: `.superpowers/research/route-c.md`
- Canonical corrections: `.superpowers/research/canonical-decisions.md`
- Durable trip constraints: `/home/shunlyu/work/private/travel_plan/CONTEXT.md`

The canonical corrections override conflicting values in the route reports.

---

### Task 1: Publish the Neutral Comparison Shell

**Files:**
- Modify: `tests/test_travel.py`
- Rewrite: `site/travel/index.html`

**Interfaces:**
- Consumes: the design and canonical comparison decisions.
- Produces: `#route-comparison`, three `data-route-choice` links, compact
  `[data-route-tabs]` controls, and stable route panel insertion points.

- [ ] **Step 1: Replace single-route tests with comparison-shell tests**

Add this module-level constant:

```python
ROUTES = {
    "route-a": ("2026.09.12–09.18", "¥26,300–46,900"),
    "route-b": ("2026.09.12–09.18", "¥25,150–30,300"),
    "route-c": ("2026.09.10–09.16", "¥24,862–40,772"),
}
```

Delete the obsolete single-itinerary page-contract methods:

```text
test_page_publishes_dated_candidate_itinerary
test_concrete_flight_schedule_candidates_are_present
test_all_seven_days_remain_in_static_html
test_booking_components_are_present
test_fallbacks_cover_fragile_decisions
test_static_supporting_route_map_remains
test_flight_and_budget_tables_have_scoped_headers
test_flight_tables_are_wrapped_for_horizontal_scroll
test_day_navigation_targets_all_days
test_dynamic_information_is_labeled_with_research_date
test_required_places_and_backup_are_present
test_supporting_route_map_ships_both_light_and_dark_variants
test_daxigou_evidence_ships_both_light_and_dark_variants
test_evidence_grid_images_load_eagerly
```

Replace `test_page_uses_local_css_js_and_local_content_images` with a narrowly
named page-asset contract that checks CSS `v=6` and JavaScript `v=4` only.
Content-image coverage returns after route panels exist. Keep the file,
noindex, privacy, social-preview, external-link safety, asset-file, CSS, and
JavaScript tests unchanged. Update the semantic-structure test to require
`header`, `main`, `section`, and `footer`; the route contract begins requiring
seven real `article` elements in Task 2.

Add:

```python
def test_page_opens_with_neutral_dense_comparison(self):
    self.assertIn("三套完整行程", self.html)
    self.assertIn('id="route-comparison"', self.html)
    self.assertIn('class="comparison-shell"', self.html)
    self.assertIn('id="comparison-title" tabindex="-1"', self.html)
    self.assertIn('class="route-comparison-wrap"', self.html)
    self.assertIn('class="route-comparison"', self.html)
    self.assertNotIn("推荐 / 最稳", self.html)
    self.assertNotIn("目前推荐 A", self.html)
    self.assertNotIn('aria-selected="true"', self.html)
    for label in ("班表已核对", "候选", "价格待确认", "条件项", "下单前复核"):
        self.assertIn(label, self.html)

def test_three_equal_route_choices_exist(self):
    choices = re.findall(r'data-route-choice="(route-[abc])"', self.html)
    self.assertEqual(choices, ["route-a", "route-b", "route-c"])
    for route_id, (dates, budget) in ROUTES.items():
        with self.subTest(route=route_id):
            self.assertIn(f'href="#{route_id}-panel"', self.html)
            self.assertIn(dates, self.html)
            self.assertIn(budget, self.html)

def test_route_b_date_disclosure_is_in_comparison_row(self):
    row = re.search(
        r'<tr[^>]*data-route-row="route-b"[^>]*>(.*?)</tr>',
        self.html,
        flags=re.DOTALL,
    )
    self.assertIsNotNone(row)
    self.assertIn(
        "个人行程 9/11 晚–9/18；新疆共同行程 9/12–9/18，7 天 6 晚",
        row.group(1),
    )

def test_compact_tabs_start_unselected(self):
    tabs = re.findall(r'<button\b[^>]*data-route-tab="route-[abc]"[^>]*>', self.html)
    self.assertEqual(len(tabs), 3)
    for tab in tabs:
        self.assertIn('aria-selected="false"', tab)
        self.assertIn('tabindex="-1"', tab)

def test_stale_single_route_values_are_removed(self):
    for fragment in (
        "2026.09.11–09.17",
        "周三 / 周五",
        "08:00</td><td>11:40",
        "11 小时 35 分",
    ):
        self.assertNotIn(fragment, self.html)
```

The rewritten shell must retain the current travel bar/footer links so the
unchanged external-link safety test remains meaningful.

- [ ] **Step 2: Run RED**

```bash
cd /home/shunlyu/work/website/homepage-travel-itinerary && python3 -m unittest tests.test_travel.TravelPageContractTests -v
```

Expected: failures for the missing comparison shell and neutral tabs.

- [ ] **Step 3: Rewrite metadata, compact summary, and comparison**

Use current CSS `v=6`, JS `v=4`, and OG `v=3`. Set the title to
`北疆 7 天三方案行程单｜航班、住宿、自驾与预算`, retain noindex/privacy/theme
bootstrap, and replace the large hero with:

```html
<section class="travel-summary" aria-labelledby="travel-title">
  <div>
    <p class="console-label">Northern Xinjiang / 3 complete plans</p>
    <h1 id="travel-title">三套完整行程，先比较，再选一套。</h1>
  </div>
  <dl class="summary-status">
    <div><dt>研究更新</dt><dd>2026-07-14</dd></div>
    <div><dt>状态</dt><dd>候选方案 · 尚未预订</dd></div>
    <div><dt>范围</dt><dd>每套 7 天 6 晚</dd></div>
  </dl>
  <p class="privacy-warning"><strong>这不是私密页面。</strong>任何拿到链接的人都能查看；页面不放身份、预订编号、电话或商务会面详情。</p>
</section>
```

Add a `route-comparison` table with the canonical A/B/C values. Use:

```html
<section id="route-comparison" class="comparison-shell" aria-labelledby="comparison-title">
  <h2 id="comparison-title" tabindex="-1">三方案比较</h2>
  <div class="route-comparison-wrap">
    <table class="route-comparison">
      <!-- caption, column headers, and the three rows below -->
    </table>
  </div>
</section>

<tr data-route-row="route-a">
  <th scope="row">A / 伊宁双翼基地</th>
  <td>2026.09.12–09.18</td><td>同行优先，经西安进出</td><td>2</td>
  <td>约 210–230 公里</td><td>2</td><td>¥26,300–46,900</td>
  <td>协调最简单</td><td>伊宁—尼勒克重复往返</td>
  <td><a href="#route-a-panel" data-route-choice="route-a">查看 A</a></td>
</tr>
<tr data-route-row="route-b">
  <th scope="row">B / 东西连续推进</th>
  <td>2026.09.12–09.18<small>个人行程 9/11 晚–9/18；新疆共同行程 9/12–9/18，7 天 6 晚</small></td>
  <td>驾驶者先到，伊宁会合</td><td>3</td>
  <td>约 300–360 公里 / 4–7 小时</td><td>1</td><td>¥25,150–30,300</td>
  <td>最像连续公路旅行</td><td>最长转场最怕天气</td>
  <td><a href="#route-b-panel" data-route-choice="route-b">查看 B</a></td>
</tr>
<tr data-route-row="route-c">
  <th scope="row">C / 唐布拉深住</th>
  <td>2026.09.10–09.16</td><td>乌鲁木齐价格优先</td><td>2</td>
  <td>无单一长途驾驶日</td><td>2</td><td>¥24,862–40,772</td>
  <td>唐布拉时间最多</td><td>返程链条最复杂</td>
  <td><a href="#route-c-panel" data-route-choice="route-c">查看 C</a></td>
</tr>
```

Add the shared GS7607 date footnote.

Below the comparison, add one compact `.status-legend` defining the five trust
labels: `班表已核对`, `候选`, `价格待确认`, `条件项`, and `下单前复核`. Retain the
existing Amap and Baidu navigation/source links with their current safe external
link attributes.

- [ ] **Step 4: Add inert-until-enhanced tab controls**

```html
<nav class="route-tabs" data-route-tabs aria-label="切换完整行程">
  <div role="tablist" aria-label="三套完整行程">
    <button type="button" role="tab" id="route-a-tab" aria-controls="route-a-panel" aria-selected="false" tabindex="-1" data-route-tab="route-a">A / 双翼基地</button>
    <button type="button" role="tab" id="route-b-tab" aria-controls="route-b-panel" aria-selected="false" tabindex="-1" data-route-tab="route-b">B / 连续推进</button>
    <button type="button" role="tab" id="route-c-tab" aria-controls="route-c-panel" aria-selected="false" tabindex="-1" data-route-tab="route-c">C / 唐布拉深住</button>
  </div>
  <a href="#route-comparison" data-route-back>返回三方案比较</a>
</nav>
```

Add `<!-- route-panels -->` after the nav as the insertion point for Tasks 2-4.

- [ ] **Step 5: Run the full suite**

```bash
cd /home/shunlyu/work/website/homepage-travel-itinerary && python3 -m unittest discover -s tests -v
```

Expected: all tests pass. No future route-panel, CSS-state, or tab-behavior tests exist yet.

- [ ] **Step 6: Commit**

```bash
cd /home/shunlyu/work/website/homepage-travel-itinerary && git add site/travel/index.html tests/test_travel.py && git commit -m "feat: add neutral three-route travel comparison"
```

---

### Task 2: Publish Route A Static Content

**Files:**
- Modify: `tests/test_travel.py`
- Modify: `site/travel/index.html`

**Interfaces:**
- Consumes: `.superpowers/research/route-a.md` and canonical corrections.
- Produces: `#route-a-panel` with all required route section classes and seven route-namespaced days.

- [ ] **Step 1: Add Route A failing tests**

Add:

```python
def route_panel(self, route_id):
    match = re.search(
        rf'<section\s+class="route-panel"\s+id="{route_id}-panel"\s+'
        rf'data-route-panel="{route_id}"\s+role="tabpanel"\s+'
        rf'aria-labelledby="{route_id}-tab">(.*?)</section>\s*<!-- /{route_id} -->',
        self.html,
        flags=re.DOTALL,
    )
    self.assertIsNotNone(match, route_id)
    return match.group(1)

def route_section(self, route_id, section_name):
    panel = self.route_panel(route_id)
    match = re.search(
        rf'<section\s+class="route-{section_name}"\s+'
        rf'aria-labelledby="{route_id}-{section_name}-title">(.*?)'
        rf'</section>\s*<!-- /{route_id}-{section_name} -->',
        panel,
        flags=re.DOTALL,
    )
    self.assertIsNotNone(match, f"{route_id} {section_name}")
    block = match.group(1)
    self.assertIn(f'id="{route_id}-{section_name}-title"', block)
    self.assertTrue(re.sub(r"<[^>]+>", "", block).strip())
    return block

def assert_complete_route(self, route_id):
    panel = self.route_panel(route_id)
    section_names = (
        "status", "flight", "transfer", "car", "map", "itinerary",
        "stays", "food", "budget", "booking", "fallbacks", "sources",
    )
    sections = {
        section_name: self.route_section(route_id, section_name)
        for section_name in section_names
    }
    positions = [
        panel.index(f'class="route-{section_name}"')
        for section_name in section_names
    ]
    self.assertEqual(positions, sorted(positions), f"{route_id} section order")
    section_fields = {
        "status": ("研究更新时间：2026-07-14", "候选", "尚未预订"),
        "flight": ("去程", "返程", "价格待确认", "下单前复核"),
        "transfer": ("接驳", "时间", "备选"),
        "car": ("取车", "还车", "驾驶者", "保险"),
        "map": ("距离", f"{route_id}.svg", f"{route_id}-dark.svg"),
        "stays": ("两间房", "主选", "备选", "可取消"),
        "food": ("早餐", "午餐", "晚餐", "清淡"),
        "budget": ("地面", "交通", "总计"),
        "booking": ("预订截止", "取消"),
        "fallbacks": ("天气", "路况", "库存", "疲劳"),
        "sources": ("href=\"https://", "班表已核对", "候选", "下单前复核"),
    }
    for section_name, required_fragments in section_fields.items():
        for fragment in required_fragments:
            self.assertIn(fragment, sections[section_name])
    for day in range(1, 8):
        article = re.search(
            rf'<article\s+class="itinerary-day"\s+id="{route_id}-day-{day}"\s+'
            rf'data-day="{day}">(.*?)</article>',
            sections["itinerary"],
            flags=re.DOTALL,
        )
        self.assertIsNotNone(article, f"{route_id} day {day}")
        for label in ("时间", "餐食", "驾驶", "体力", "备选"):
            self.assertIn(label, article.group(1))
    dates, budget = ROUTES[route_id]
    for fragment in (
        dates,
        budget,
        "可取消",
        "预订截止",
        "下单前复核",
    ):
        self.assertIn(fragment, panel)
    for forbidden_reference in ("同 A", "同 B", "同 C", "见上方", "共用前述"):
        self.assertNotIn(forbidden_reference, panel)

def test_route_a_is_complete_and_canonical(self):
    self.assert_complete_route("route-a")
    panel = self.route_panel("route-a")
    for fragment in (
        "GS7607", "周二、周四、周六",
        "6 小时 14 分计划间隔", "约 5–5.5 小时可用时间",
        "西安住宿一晚", "约 210–230 公里 / 3–3.5 小时",
        "每日西安—伊宁航线走廊", "具体航班号与时刻下单前复核",
        "¥26,300–46,900", "route-a.svg", "route-a-dark.svg",
    ):
        self.assertIn(fragment, panel)
    self.assertNotRegex(
        panel,
        r"3U50(?:39|40)[\s\S]{0,300}班表已核对",
        "unconfirmed 3U times must not be labeled as verified",
    )
```

- [ ] **Step 2: Run RED**

```bash
cd /home/shunlyu/work/website/homepage-travel-itinerary && python3 -m unittest tests.test_travel.TravelPageContractTests.test_route_a_is_complete_and_canonical -v
```

- [ ] **Step 3: Insert Route A**

Insert a static `#route-a-panel` at `<!-- route-panels -->`, using every
route-specific section from Route A research and canonical corrections.
Use this exact outer contract:

```html
<section class="route-panel" id="route-a-panel"
         data-route-panel="route-a" role="tabpanel"
         aria-labelledby="route-a-tab">
  <!-- the 12 required route sections in design-spec order -->
</section><!-- /route-a -->
```

Use the same ordered attributes and namespaced IDs for Routes B and C. Every
day is an `<article class="itinerary-day">` and explicitly labels time, meals,
driving, effort, and fallback. Each of the 12 subsections uses
`class="route-{section}"`, `aria-labelledby="route-a-{section}-title"`, a
matching namespaced heading ID, and a closing marker such as
`<!-- /route-a-flight -->`; apply the same convention to B and C.

Use 2 bases, 2 rooms, Hampton Yining, Bee Town, the seven dated days,
conditional Daxigou, candidate daily XIY↔YIN return corridor, the safer Xi'an
overnight, budget `¥26,300–46,900`, and route A light/dark maps.

- [ ] **Step 4: Run full tests**

```bash
cd /home/shunlyu/work/website/homepage-travel-itinerary && python3 -m unittest discover -s tests -v
```

Expected: all tests pass.

- [ ] **Step 5: Commit**

```bash
cd /home/shunlyu/work/website/homepage-travel-itinerary && git add site/travel/index.html tests/test_travel.py && git commit -m "feat: add coordination-first route itinerary"
```

---

### Task 3: Publish Route B Static Content

**Files:**
- Modify: `tests/test_travel.py`
- Modify: `site/travel/index.html`

**Interfaces:**
- Consumes: `.superpowers/research/route-b.md` and canonical corrections.
- Produces: `#route-b-panel`, seven route-namespaced days, split-arrival logistics, and conservative long-transfer safety copy.

- [ ] **Step 1: Add Route B failing tests**

```python
def test_route_b_is_complete_and_canonical(self):
    self.assert_complete_route("route-b")
    panel = self.route_panel("route-b")
    for fragment in (
        "MU6903", "CZ6823", "GS7607", "约 20 分钟",
        "商务出行者个人行程为 9 月 11 日晚至 9 月 18 日",
        "约 300–360 公里 / 4–7 小时",
        "不进入仙女湖高海拔段",
        "¥25,150–30,300", "route-b.svg", "route-b-dark.svg",
    ):
        self.assertIn(fragment, panel)
    self.assertNotIn("骑马上山", panel)
    self.assertNotIn("延长至仙女湖", panel)
```

- [ ] **Step 2: Run RED**

```bash
cd /home/shunlyu/work/website/homepage-travel-itinerary && python3 -m unittest tests.test_travel.TravelPageContractTests.test_route_b_is_complete_and_canonical -v
```

- [ ] **Step 3: Insert Route B**

Insert `#route-b-panel` after Route A. Use the driver-pair Urumqi chain,
business-traveler Xi'an D-1 overnight, 20-minute reunion gap, Yining +
Qingshuihe/Huocheng + Bee Town bases, the conservative 300–360 km Day 3, seven
dated days, no horse or Fairy Lake extension, budget `¥25,150–30,300`, and
route B light/dark maps.

- [ ] **Step 4: Run full tests**

```bash
cd /home/shunlyu/work/website/homepage-travel-itinerary && python3 -m unittest discover -s tests -v
```

- [ ] **Step 5: Commit**

```bash
cd /home/shunlyu/work/website/homepage-travel-itinerary && git add site/travel/index.html tests/test_travel.py && git commit -m "feat: add time-first continuous route itinerary"
```

---

### Task 4: Publish Route C and Complete the Static Contract

**Files:**
- Modify: `tests/test_travel.py`
- Modify: `site/travel/index.html`

**Interfaces:**
- Consumes: `.superpowers/research/route-c.md` and canonical corrections.
- Produces: `#route-c-panel`, all three complete static panels, and compact shared evidence appendix.

- [ ] **Step 1: Add Route C and aggregate failing tests**

```python
def test_route_c_is_complete_and_canonical(self):
    self.assert_complete_route("route-c")
    panel = self.route_panel("route-c")
    for fragment in (
        "C848", "14:08 / 14:17", "16:30 以后",
        "CZ6853", "优先候选", "技术经停待确认",
        "14:00 方案降级为备选", "约 4–4.5 小时可用时间",
        "不抵达仙女湖", "湿滑溪流石面",
        "¥24,862–40,772", "约 ¥1,000–2,300",
        "route-c.svg", "route-c-dark.svg",
    ):
        self.assertIn(fragment, panel)
    self.assertRegex(
        panel,
        r"CZ6853[\s\S]{0,500}下单前复核",
        "CZ6853 must carry its own nearby verification warning",
    )

def test_all_three_static_panels_are_independent(self):
    for route_id in ROUTES:
        self.assert_complete_route(route_id)
    ids = re.findall(r'\bid="([^"]+)"', self.html)
    self.assertEqual(len(ids), len(set(ids)))

def test_all_operational_tables_have_scoped_column_headers(self):
    tables = re.findall(r"<table\b[^>]*>(.*?)</table>", self.html, flags=re.DOTALL)
    self.assertGreaterEqual(len(tables), 10)
    for table in tables:
        with self.subTest(table=table[:80]):
            self.assertIn('scope="col"', table)

def test_all_flight_tables_have_local_scroll_wrappers(self):
    flight_sections = re.findall(
        r'<section\b[^>]*class="route-flight[^"]*"[^>]*>(.*?)</section>',
        self.html,
        flags=re.DOTALL,
    )
    self.assertEqual(len(flight_sections), 3)
    for section in flight_sections:
        self.assertRegex(section, r'<div class="matrix-wrap">\s*<table\b')

def test_all_content_images_are_local_and_theme_pairs_are_complete(self):
    image_sources = re.findall(r'<img\b[^>]*\bsrc="([^"]+)"', self.html)
    self.assertTrue(image_sources)
    for source in image_sources:
        self.assertTrue(source.startswith("/travel/assets/"), source)
    for route_id in ROUTES:
        panel = self.route_panel(route_id)
        self.assertIn(f'src="/travel/assets/{route_id}.svg"', panel)
        self.assertIn(f'src="/travel/assets/{route_id}-dark.svg"', panel)

def test_shared_evidence_keeps_theme_variants_and_eager_loading(self):
    appendix = re.search(
        r'<aside class="shared-appendix"[^>]*>(.*?)</aside>',
        self.html,
        flags=re.DOTALL,
    )
    self.assertIsNotNone(appendix)
    block = appendix.group(1)
    self.assertIn("daxigou-evidence.svg", block)
    self.assertIn("daxigou-evidence-dark.svg", block)
    for image in re.findall(r"<img\b[^>]*>", block):
        self.assertNotIn('loading="lazy"', image)
```

- [ ] **Step 2: Run RED**

```bash
cd /home/shunlyu/work/website/homepage-travel-itinerary && python3 -m unittest tests.test_travel.TravelPageContractTests.test_route_c_is_complete_and_canonical tests.test_travel.TravelPageContractTests.test_all_three_static_panels_are_independent -v
```

- [ ] **Step 3: Insert Route C**

Insert `#route-c-panel` after Route B. Use the Sep 10–16 Urumqi gateway,
same-day outbound flight transfer, four Bee Town nights, C848 return, 16:30
flight floor, CZ6853 as the preferred candidate with a technical-stop
verification warning, the 14:00 option demoted to fallback with only
`约 4–4.5 小时可用时间`, truncated sub-2,200m hike with wet-rock caveat,
low-confidence Sep 15 Daxigou, budget `¥24,862–40,772`, and route C light/dark
maps.

- [ ] **Step 4: Keep the shared evidence appendix compact**

Retain licensed Tangbula, Yining, Daxigou, and Kuerdening evidence in:

```html
<aside class="shared-appendix" aria-labelledby="evidence-title">
  <!-- compact existing evidence grid and attribution links -->
</aside>
```

Every route panel still contains its own operational sources; the shared
appendix is supplementary only.

- [ ] **Step 5: Run focused and full tests**

```bash
cd /home/shunlyu/work/website/homepage-travel-itinerary && python3 -m unittest tests.test_travel.TravelPageContractTests tests.test_travel.TravelAssetTests -v && python3 -m unittest discover -s tests -v
```

Expected: all tests pass.

- [ ] **Step 6: Commit**

```bash
cd /home/shunlyu/work/website/homepage-travel-itinerary && git add site/travel/index.html tests/test_travel.py && git commit -m "feat: complete three-route travel content"
```

---

### Task 5: Implement the High-Density Screen and Print Layout

**Files:**
- Modify: `tests/test_travel.py`
- Modify: `site/travel/index.html`
- Rewrite: `site/travel/travel.css`

**Interfaces:**
- Consumes: `.route-comparison-wrap`, `.route-comparison`, `.route-tabs`,
  `.comparison-shell`, `.shared-appendix`, `[data-route-panel]`, route section classes, and root
  `data-route-enhanced`/`data-active-route` attributes.
- Produces: dense desktop/mobile layout, the complete no-JavaScript/comparison/
  selected-route state matrix, CSS asset version `v=7`, and three-state print
  behavior used by Task 6.

- [ ] **Step 1: Add failing density and route-state style tests**

Add:

```python
def test_dense_comparison_and_route_panels_are_scoped(self):
    required = (
        "html.travel-page .comparison-shell",
        "html.travel-page .route-comparison-wrap",
        "html.travel-page .route-comparison",
        "html.travel-page .route-tabs",
        'html.travel-page[data-route-enhanced="true"][data-active-route^="route-"] .route-tabs',
        "html.travel-page .route-panel",
        'html.travel-page[data-route-enhanced="true"][data-active-route="comparison"] .comparison-shell',
        'html.travel-page[data-route-enhanced="true"][data-active-route^="route-"] .comparison-shell',
        'html.travel-page[data-route-enhanced="true"][data-active-route="route-a"] #route-a-panel',
        'html.travel-page[data-route-enhanced="true"][data-active-route="route-b"] #route-b-panel',
        'html.travel-page[data-route-enhanced="true"][data-active-route="route-c"] #route-c-panel',
    )
    for selector in required:
        with self.subTest(selector=selector):
            self.assertIn(selector, self.css)

def test_layout_uses_dense_spacing_and_wide_comparison_width(self):
    self.assertIn("--content-width: 90rem", self.css)
    self.assertIn("--space-1: 0.375rem", self.css)
    self.assertIn("--space-2: 0.625rem", self.css)
    self.assertNotIn("min-height: 70vh", self.css)
    self.assertNotIn("font-size: clamp(3rem", self.css)

def test_mobile_contains_comparison_and_tabs_without_page_overflow(self):
    mobile = self.css.split("@media (max-width: 760px) {", 1)[1]
    self.assertIn(".route-comparison-wrap", mobile)
    self.assertIn("overflow-x: auto", mobile)
    self.assertIn(".route-tabs", mobile)
    self.assertIn("overflow-x: auto", mobile)

def test_print_selects_active_route_or_comparison(self):
    print_block = self.css.split("@media print {", 1)[1]
    for fragment in (
        '[data-route-enhanced="true"][data-active-route="comparison"] .route-panel',
        '[data-route-enhanced="true"][data-active-route="comparison"] .shared-appendix',
        '[data-route-enhanced="true"][data-active-route^="route-"] .comparison-shell',
        '[data-route-enhanced="true"][data-active-route^="route-"] .shared-appendix',
        '[data-route-enhanced="true"][data-active-route="route-a"] .route-panel:not(#route-a-panel)',
        '[data-route-enhanced="true"][data-active-route="route-b"] .route-panel:not(#route-b-panel)',
        '[data-route-enhanced="true"][data-active-route="route-c"] .route-panel:not(#route-c-panel)',
        ".route-panel + .route-panel",
        "break-before: page",
    ):
        self.assertIn(fragment, print_block)

```

Update the existing page asset-version tests to expect CSS `v=7`, JavaScript
`v=4`, and OG `v=3`; do not add a second overlapping version test.

- [ ] **Step 2: Run RED**

```bash
cd /home/shunlyu/work/website/homepage-travel-itinerary && python3 -m unittest tests.test_travel.TravelStyleTests -v
```

Expected: failures for the new comparison, active-route, dense-spacing, mobile,
and print selectors.

- [ ] **Step 3: Replace the large-page spacing with dense tokens**

Keep the existing light/dark theme values, focus ring, reduced-motion rules,
theme-image rules, image-failure rules, and forced-light print tokens.

Add:

```css
html.travel-page {
  --content-width: 90rem;
  --space-1: 0.375rem;
  --space-2: 0.625rem;
  --space-3: 1rem;
  --space-4: 1.5rem;
}

html.travel-page main,
html.travel-page .travel-bar__inner,
html.travel-page .travel-footer {
  width: min(calc(100% - 2rem), var(--content-width));
}

html.travel-page main {
  gap: var(--space-4);
  padding-block: var(--space-3) var(--space-4);
}

html.travel-page section {
  padding-block: var(--space-3);
}
```

Remove large hero-height, decorative card-grid, and oversized section-gap rules.

- [ ] **Step 4: Style the comparison as a flat decision table**

```css
html.travel-page .route-comparison-wrap,
html.travel-page .matrix-wrap,
html.travel-page .budget-wrap {
  overflow-x: auto;
  border: 1px solid var(--hairline);
  background: var(--panel-bg);
}

html.travel-page .route-comparison {
  min-width: 72rem;
}

html.travel-page .route-comparison th,
html.travel-page .route-comparison td {
  padding: 0.55rem 0.65rem;
  vertical-align: top;
}

html.travel-page .route-comparison tbody tr:hover {
  background: color-mix(in srgb, var(--signal) 8%, transparent);
}

html.travel-page .route-comparison small {
  display: block;
  margin-top: 0.25rem;
  color: var(--page-muted);
}
```

- [ ] **Step 5: Style compact tabs and route sections**

Implement this state matrix exactly:

| State | Comparison | Tabs | Route panels | Shared appendix |
|---|---|---|---|---|
| No JavaScript | Visible | Hidden | All visible | Visible |
| Enhanced comparison | Visible | Hidden | All hidden | Hidden |
| Enhanced selected route | Hidden | Visible | Exactly one visible | Hidden |

```css
html.travel-page .route-tabs {
  display: none;
  position: sticky;
  top: var(--bar-height);
  z-index: 8;
  align-items: stretch;
  justify-content: space-between;
  gap: var(--space-2);
  overflow-x: auto;
  border-block: 1px solid var(--hairline);
  background: var(--page-bg);
}

html.travel-page .route-tabs [role="tablist"] {
  display: flex;
  min-width: max-content;
}

html.travel-page .route-tabs button,
html.travel-page .route-tabs a {
  min-height: 2.75rem;
  padding: 0.6rem 0.85rem;
  border: 0;
  border-bottom: 3px solid transparent;
  background: transparent;
  color: inherit;
  font: inherit;
}

html.travel-page[data-route-enhanced="true"][data-active-route^="route-"] .route-tabs {
  display: flex;
}

html.travel-page .route-tabs button[aria-selected="true"] {
  border-bottom-color: var(--signal);
  font-weight: 700;
}

html.travel-page .route-panel {
  display: block;
}

html.travel-page[data-route-enhanced="true"] .route-panel {
  display: none;
}

html.travel-page[data-route-enhanced="true"][data-active-route="comparison"] .comparison-shell {
  display: block;
}

html.travel-page[data-route-enhanced="true"][data-active-route^="route-"] .comparison-shell,
html.travel-page[data-route-enhanced="true"] .shared-appendix {
  display: none;
}

html.travel-page[data-route-enhanced="true"][data-active-route="route-a"] #route-a-panel,
html.travel-page[data-route-enhanced="true"][data-active-route="route-b"] #route-b-panel,
html.travel-page[data-route-enhanced="true"][data-active-route="route-c"] #route-c-panel {
  display: block;
}
```

Style route facts as compact definition grids, day entries as ruled blocks, and
flight/stay/budget tables as flat bordered tables. Do not add decorative shadows.

- [ ] **Step 6: Implement mobile behavior**

Inside `@media (max-width: 760px)`:

```css
html.travel-page .route-comparison-wrap,
html.travel-page .route-tabs,
html.travel-page .matrix-wrap,
html.travel-page .budget-wrap {
  overflow-x: auto;
}

html.travel-page .route-tabs {
  margin-inline: -1rem;
  padding-inline: 1rem;
}

html.travel-page .route-facts,
html.travel-page .route-section-grid {
  grid-template-columns: 1fr;
}
```

Keep minimum 44px coarse-pointer targets.

- [ ] **Step 7: Implement selected-route print**

Preserve the existing forced-light token reset, light-image forcing, full-width
flight-table rules, skip-link hiding, and fixed/sticky positioning defenses.

Add:

```css
@media print {
  html.travel-page .route-tabs,
  html.travel-page .travel-bar,
  html.travel-page .skip-link,
  html.travel-page .travel-footer {
    display: none !important;
    position: static !important;
  }

  html.travel-page[data-route-enhanced="true"][data-active-route="comparison"] .route-panel {
    display: none !important;
  }

  html.travel-page[data-route-enhanced="true"][data-active-route="comparison"] .shared-appendix,
  html.travel-page[data-route-enhanced="true"][data-active-route^="route-"] .comparison-shell,
  html.travel-page[data-route-enhanced="true"][data-active-route^="route-"] .shared-appendix {
    display: none !important;
  }

  html.travel-page[data-route-enhanced="true"][data-active-route="route-a"] .route-panel:not(#route-a-panel),
  html.travel-page[data-route-enhanced="true"][data-active-route="route-b"] .route-panel:not(#route-b-panel),
  html.travel-page[data-route-enhanced="true"][data-active-route="route-c"] .route-panel:not(#route-c-panel) {
    display: none !important;
  }

  html.travel-page:not([data-route-enhanced="true"]) .route-panel + .route-panel {
    break-before: page;
  }

  html.travel-page .itinerary-day {
    display: block;
    break-inside: avoid;
  }
}
```

- [ ] **Step 8: Bump only the changed CSS asset**

Change the stylesheet URL in `site/travel/index.html` from `travel.css?v=6` to
`travel.css?v=7`. Keep JavaScript at `v=4` and the social preview at `v=3`.
Update the asset-version contract test accordingly.

- [ ] **Step 9: Run focused and full tests**

```bash
cd /home/shunlyu/work/website/homepage-travel-itinerary && python3 -m unittest tests.test_travel.TravelStyleTests -v && python3 -m unittest discover -s tests -v
```

Expected: style and content tests pass; only new Task 6 script tests are not yet present.

- [ ] **Step 10: Commit**

```bash
cd /home/shunlyu/work/website/homepage-travel-itinerary && git add site/travel/index.html site/travel/travel.css tests/test_travel.py && git commit -m "feat: style dense three-route travel comparison"
```

---

### Task 6: Add Accessible Hash-Addressable Route Tabs

**Files:**
- Modify: `tests/test_travel.py`
- Modify: `site/travel/index.html`
- Modify: `site/travel/travel.js`

**Interfaces:**
- Consumes: comparison links, `[data-route-tabs]`, `[data-route-tab]`,
  `[data-route-back]`, and route IDs from Task 1 plus the three
  `[data-route-panel]` sections from Tasks 2-4.
- Produces: `initRouteTabs()`, root `data-route-enhanced`, root
  `data-active-route`, hash synchronization, tab keyboard behavior, focus return,
  and JavaScript asset version `v=5`.

- [ ] **Step 1: Add failing script-contract tests**

Update `test_defines_only_required_initializers`:

```python
for name in ("initThemeControl", "initImageFailureState", "initRouteTabs"):
    self.assertRegex(self.js, rf"function\s+{name}\s*\(")
```

Add:

```python
def test_route_tabs_use_static_content_as_progressive_enhancement(self):
    self.assertIn("data-route-enhanced", self.js)
    self.assertIn("data-active-route", self.js)
    self.assertNotIn("innerHTML", self.js)
    self.assertNotIn("insertAdjacentHTML", self.js)
    self.assertNotIn("panel.remove()", self.js)

def test_route_tabs_support_hash_and_comparison_state(self):
    for fragment in (
        "window.location.hash",
        "history.replaceState",
        "hashchange",
        "route-a",
        "route-b",
        "route-c",
        "comparison",
    ):
        self.assertIn(fragment, self.js)
    self.assertIn("-panel", self.js)

def test_route_tabs_support_keyboard_navigation(self):
    for key in ("ArrowLeft", "ArrowRight", "Home", "End"):
        self.assertIn(key, self.js)
    self.assertIn("aria-selected", self.js)
    self.assertIn("tabIndex", self.js)
    self.assertIn(".focus()", self.js)
```

- [ ] **Step 2: Run RED**

```bash
cd /home/shunlyu/work/website/homepage-travel-itinerary && python3 -m unittest tests.test_travel.TravelScriptTests -v
```

Expected: failures because `initRouteTabs` and its state/hash/keyboard behavior do not exist.

- [ ] **Step 3: Implement route-tab initialization**

Add this function before the final initializer calls:

```javascript
function initRouteTabs() {
  var root = document.documentElement;
  var routeIds = ['route-a', 'route-b', 'route-c'];
  var choices = Array.from(document.querySelectorAll('[data-route-choice]'));
  var tabs = Array.from(document.querySelectorAll('[data-route-tab]'));
  var panels = Array.from(document.querySelectorAll('[data-route-panel]'));
  var tabBar = document.querySelector('[data-route-tabs]');
  var backLink = document.querySelector('[data-route-back]');
  var comparisonTitle = document.querySelector('#comparison-title');

  if (
    choices.length !== routeIds.length ||
    tabs.length !== routeIds.length ||
    panels.length !== routeIds.length ||
    !tabBar ||
    !backLink ||
    !comparisonTitle
  ) {
    return;
  }

  function routeFromHash() {
    var value = window.location.hash.replace(/^#/, '');
    var fallbackRoute = value.replace(/-panel$/, '');
    if (routeIds.indexOf(value) !== -1) return value;
    if (routeIds.indexOf(fallbackRoute) !== -1) return fallbackRoute;
    return 'comparison';
  }

  function setTabState(routeId) {
    tabs.forEach(function (tab) {
      var active = tab.getAttribute('data-route-tab') === routeId;
      tab.setAttribute('aria-selected', String(active));
      tab.tabIndex = active ? 0 : -1;
    });
  }

  function activate(routeId, updateHash, focusTab) {
    var next = routeIds.indexOf(routeId) === -1 ? 'comparison' : routeId;
    root.setAttribute('data-active-route', next);
    setTabState(next);

    if (updateHash) {
      var hash = next === 'comparison' ? window.location.pathname + window.location.search : '#' + next;
      history.replaceState(null, '', hash);
    }

    if (focusTab && next !== 'comparison') {
      tabs[routeIds.indexOf(next)].focus();
    }
  }

  choices.forEach(function (choice) {
    choice.addEventListener('click', function (event) {
      event.preventDefault();
      activate(choice.getAttribute('data-route-choice'), true, true);
    });
  });

  tabs.forEach(function (tab, index) {
    tab.addEventListener('click', function () {
      activate(tab.getAttribute('data-route-tab'), true, false);
    });

    tab.addEventListener('keydown', function (event) {
      var nextIndex = index;
      if (event.key === 'ArrowLeft') nextIndex = (index - 1 + tabs.length) % tabs.length;
      if (event.key === 'ArrowRight') nextIndex = (index + 1) % tabs.length;
      if (event.key === 'Home') nextIndex = 0;
      if (event.key === 'End') nextIndex = tabs.length - 1;
      if (nextIndex === index && event.key !== 'Home' && event.key !== 'End') return;
      event.preventDefault();
      activate(tabs[nextIndex].getAttribute('data-route-tab'), true, true);
    });
  });

  backLink.addEventListener('click', function (event) {
    event.preventDefault();
    activate('comparison', true, false);
    comparisonTitle.focus();
  });

  window.addEventListener('hashchange', function () {
    activate(routeFromHash(), /-panel$/.test(window.location.hash), false);
  });

  root.setAttribute('data-route-enhanced', 'true');
  var initialRoute = routeFromHash();
  activate(initialRoute, /-panel$/.test(window.location.hash), false);
}
```

Task 1 already gives `#comparison-title` `tabindex="-1"`; preserve it.

- [ ] **Step 4: Call the initializer**

The IIFE tail becomes:

```javascript
initThemeControl();
initImageFailureState();
initRouteTabs();
```

- [ ] **Step 5: Bump only the changed JavaScript asset**

Change the script URL in `site/travel/index.html` from `travel.js?v=4` to
`travel.js?v=5`. Keep CSS at `v=7` and the social preview at `v=3`. Update the
existing page asset-version test accordingly.

- [ ] **Step 6: Run focused and full tests**

```bash
cd /home/shunlyu/work/website/homepage-travel-itinerary && node --check site/travel/travel.js && python3 -m unittest tests.test_travel.TravelScriptTests -v && python3 -m unittest discover -s tests -v
```

Expected: JavaScript syntax succeeds and all tests pass.

- [ ] **Step 7: Prove the state machine in a real Playwright runtime**

Start the static server:

```bash
cd /home/shunlyu/work/website/homepage-travel-itinerary && python3 -m http.server 8094 --directory site
```

Use Playwright against `http://127.0.0.1:8094/travel/` and execute assertions
that throw on failure:

```javascript
() => {
 const root = document.documentElement;
 const visible = (element) => getComputedStyle(element).display !== 'none';
 const panels = [...document.querySelectorAll('[data-route-panel]')];
 const comparison = document.querySelector('.comparison-shell');
 const tabs = document.querySelector('[data-route-tabs]');
 if (root.dataset.activeRoute !== 'comparison') throw new Error('initial state');
 if (!visible(comparison) || visible(tabs)) throw new Error('comparison visibility');
 if (panels.some(visible)) throw new Error('panels visible in comparison state');
}
```

Then:

1. Click each comparison link and assert the canonical URL hash is `#route-a`,
  `#route-b`, or `#route-c`, the comparison is hidden, the tabs are visible,
  exactly one matching panel is visible, and exactly one tab has
  `aria-selected="true"`.
2. Load `#route-a`, `#route-b`, `#route-c`, and fallback `#route-c-panel`
  directly and assert the matching route opens; the fallback URL is canonicalized
  to `#route-c`.
3. Load `#invalid` and assert the neutral comparison state.
4. Exercise Arrow Left/Right, Home, and End and assert both focus and selected
  route change.
5. Activate “返回三方案比较” and assert the hash is removed, the comparison is
  visible, all panels are hidden, and `#comparison-title` owns focus.
6. Disable JavaScript in a fresh context and assert the comparison and all three
  panels are visible, tabs are hidden, and `href="#route-a-panel"` reaches the
  Route A panel.

Stop the static server after the assertions.

- [ ] **Step 8: Commit**

```bash
cd /home/shunlyu/work/website/homepage-travel-itinerary && git add site/travel/index.html site/travel/travel.js tests/test_travel.py && git commit -m "feat: add accessible travel route tabs"
```

---

### Task 7: Refresh Public Context and Three-Plan Share Preview

**Files:**
- Modify: `/home/shunlyu/work/private/travel_plan/CONTEXT.md`
- Modify: `tests/test_travel.py`
- Modify: `site/travel/index.html`
- Modify: `site/travel/assets/og-travel.svg`
- Regenerate: `site/travel/assets/og-travel.png`

**Interfaces:**
- Consumes: the final three-route page framing.
- Produces: durable private context, a 1200×630 preview matching the public page,
  and social-preview asset version `v=4`.

- [ ] **Step 1: Add failing OG copy tests**

Extend `TravelAssetTests`:

```python
def test_social_preview_describes_three_complete_plans(self):
    svg = (ASSETS / "og-travel.svg").read_text(encoding="utf-8")
    for fragment in (
        "NORTHERN XINJIANG",
        "3 COMPLETE PLANS",
        "A BASE · B CONTINUOUS · C DEEP STAY",
        "NOT BOOKED",
    ):
        self.assertIn(fragment, svg)
    self.assertNotIn("飞机、住宿、每天怎么走", svg)
```

Update
`TravelPageContractTests.test_social_preview_uses_current_cache_buster` to
expect `og-travel.png?v=4`. Keep the existing page CSS/JavaScript asset test at
CSS `v=7` and JavaScript `v=5`.

- [ ] **Step 2: Run RED**

```bash
cd /home/shunlyu/work/website/homepage-travel-itinerary && python3 -m unittest tests.test_travel.TravelAssetTests.test_social_preview_describes_three_complete_plans tests.test_travel.TravelPageContractTests.test_social_preview_uses_current_cache_buster -v
```

Expected: failure because the preview still describes one itinerary.

- [ ] **Step 3: Update durable private context**

Replace the `Dated Primary Itinerary` entry with:

```markdown
**Three Complete Itinerary Candidates**:
The public page presents three independently actionable seven-day candidates:
Route A uses a stable Yining double-wing base and coordination-first flights;
Route B uses a west-to-east continuous road trip and time-first split arrivals;
Route C uses a Tangbula deep stay and price-first Urumqi gateway. The page opens
with a neutral, high-density comparison and does not recommend or preselect a route.
_Avoid_: Single primary itinerary, abbreviated alternatives, decorative route cards
```

Add:

```markdown
**High-Density Travel Page**:
The travel page prioritizes compact comparison tables, timelines, operational
details, and decision-critical caveats over visual presentation, large cards,
marketing copy, or decorative spacing.
_Avoid_: Design-led landing page, oversized hero, low-information cards
```

Verify the private context immediately:

```bash
cd /home/shunlyu/work/website/homepage-travel-itinerary && rg -F "Three Complete Itinerary Candidates" /home/shunlyu/work/private/travel_plan/CONTEXT.md && rg -F "High-Density Travel Page" /home/shunlyu/work/private/travel_plan/CONTEXT.md && ! rg -F "Dated Primary Itinerary" /home/shunlyu/work/private/travel_plan/CONTEXT.md
```

- [ ] **Step 4: Update the SVG copy**

Keep the existing background, grid, route path, and circles. Replace only the
text with:

```xml
<text ...>NORTHERN XINJIANG</text>
<text ...>3 COMPLETE PLANS</text>
<text ...>A BASE · B CONTINUOUS · C DEEP STAY</text>
<text ...>NOT BOOKED</text>
```

- [ ] **Step 5: Regenerate and verify the PNG**

```bash
cd /home/shunlyu/work/website/homepage-travel-itinerary && rsvg-convert -w 1200 -h 630 site/travel/assets/og-travel.svg -o site/travel/assets/og-travel.png && file site/travel/assets/og-travel.png
```

Expected: `PNG image data, 1200 x 630`.

- [ ] **Step 6: Bump only the changed social-preview asset**

Change the Open Graph and Twitter image URLs in `site/travel/index.html` from
`og-travel.png?v=3` to `og-travel.png?v=4`. Keep CSS at `v=7` and JavaScript at
`v=5`.

- [ ] **Step 7: Run focused and full tests**

```bash
cd /home/shunlyu/work/website/homepage-travel-itinerary && python3 -m unittest tests.test_travel.TravelAssetTests -v && python3 -m unittest discover -s tests -v
```

Expected: all tests pass.

- [ ] **Step 8: Commit tracked files**

```bash
cd /home/shunlyu/work/website/homepage-travel-itinerary && git add site/travel/index.html site/travel/assets/og-travel.svg site/travel/assets/og-travel.png tests/test_travel.py && git commit -m "docs: align travel preview with three-route comparison"
```

The private `CONTEXT.md` is outside Git and must not be staged.

---

### Task 8: Browser Review, Deploy, and Verify

**Files:**
- Verify: all changed travel files and private context.
- Do not modify: `/home/shunlyu/work/website/homepage/.gitignore`.

**Interfaces:**
- Consumes: complete static bundle from Tasks 1-7.
- Produces: verified live `https://shunlyu.com/travel/`.

- [ ] **Step 1: Run final repository checks**

```bash
cd /home/shunlyu/work/website/homepage-travel-itinerary && git status --short --branch && git --no-pager diff main...HEAD --stat && python3 -m unittest discover -s tests -v && node --check site/travel/travel.js && rg -F "Three Complete Itinerary Candidates" /home/shunlyu/work/private/travel_plan/CONTEXT.md && rg -F "High-Density Travel Page" /home/shunlyu/work/private/travel_plan/CONTEXT.md && ! rg -F "Dated Primary Itinerary" /home/shunlyu/work/private/travel_plan/CONTEXT.md
```

Expected: all tests pass, JavaScript syntax passes, and only planned travel,
test, design, and plan files differ.

- [ ] **Step 2: Inspect a local static server with Playwright**

Start:

```bash
cd /home/shunlyu/work/website/homepage-travel-itinerary && python3 -m http.server 8094 --directory site
```

Inspect:

1. 1440×1000 comparison state: no active route, dense table above the fold.
2. A/B/C direct hashes: correct panel and selected tab.
3. Every route: flights, transfer, car, map, seven days, stays, food, budget,
   booking, fallbacks, sources.
4. Route B: extra-day disclosure and 300–360 km caveat.
5. Route C: 16:30 flight floor and CZ6853 technical-stop warning.
6. Mobile 390×844: no page-level overflow; comparison/table/tab wrappers scroll.
7. Explicit dark and OS-auto dark screen modes.
8. Print comparison: summaries only.
9. Print A, B, and C: only selected panel, complete tables, light theme.
10. JavaScript disabled: all three panels visible and comparison links work.
11. JavaScript-disabled print: create a fresh Playwright context with
    `javaScriptEnabled: false`, emulate `media: "print"`, assert the comparison
    and all three route headings are visible, assert Route B and C compute
    `break-before: page`, generate a PDF inside the feature worktree, and inspect
    that all three routes are present on separate route starts.
12. Invalid hash: neutral comparison.
13. Arrow Left/Right and Home/End keyboard tab navigation.

Stop the server and remove temporary screenshots/PDFs.

- [ ] **Step 3: Review the complete branch before deployment**

Request a whole-branch code review from `main` to `HEAD`. Fix every Critical or
Important finding, commit each fix, and rerun Step 1 plus every relevant
assertion in Step 2. Re-request whole-branch review on the new `HEAD` until no
Critical or Important finding remains. Then require a clean tracked worktree and
record the reviewed commit in a dedicated local Git ref:

```bash
cd /home/shunlyu/work/website/homepage-travel-itinerary && git diff --quiet && git diff --cached --quiet && test -z "$(git status --porcelain --untracked-files=all -- site Containerfile)" && git update-ref refs/reviews/travel-itinerary "$(git rev-parse HEAD)" && git rev-parse refs/reviews/travel-itinerary
```

Do not build or restart production before this gate passes.

- [ ] **Step 4: Fast-forward local main to the reviewed commit**

Record the checksum of the main checkout's existing `.gitignore` diff, perform a
non-interactive fast-forward, verify the checksum is unchanged, and assert both
worktrees point at the same reviewed commit:

```bash
cd /home/shunlyu/work/website/homepage-travel-itinerary && reviewed_sha="$(git rev-parse refs/reviews/travel-itinerary)" && test "$(git rev-parse HEAD)" = "$reviewed_sha" && before="$(git -C /home/shunlyu/work/website/homepage diff -- .gitignore | sha256sum | cut -d' ' -f1)" && git -C /home/shunlyu/work/website/homepage merge --ff-only "$reviewed_sha" && after="$(git -C /home/shunlyu/work/website/homepage diff -- .gitignore | sha256sum | cut -d' ' -f1)" && test "$before" = "$after" && test "$reviewed_sha" = "$(git -C /home/shunlyu/work/website/homepage rev-parse HEAD)" && git -C /home/shunlyu/work/website/homepage status --short --branch
```

- [ ] **Step 5: Build and restart the reviewed commit**

```bash
cd /home/shunlyu/work/website/homepage-travel-itinerary && reviewed_sha="$(git rev-parse refs/reviews/travel-itinerary)" && test "$(git rev-parse HEAD)" = "$reviewed_sha" && test "$reviewed_sha" = "$(git -C /home/shunlyu/work/website/homepage rev-parse HEAD)" && test -z "$(git status --porcelain --untracked-files=all -- site Containerfile)" && podman build -t localhost/shunlyu-homepage:latest -f Containerfile . && systemctl --user restart shunlyu-homepage.service && systemctl --user is-active shunlyu-homepage.service
```

Expected: `active`.

- [ ] **Step 6: Verify local container output**

```bash
cd /home/shunlyu/work/website/homepage-travel-itinerary && curl -fsS http://127.0.0.1:8081/travel/ | grep -F "三套完整行程" && curl -fsS http://127.0.0.1:8081/travel/ | grep -F "¥26,300–46,900" && curl -fsS http://127.0.0.1:8081/travel/ | grep -F "¥25,150–30,300" && curl -fsS http://127.0.0.1:8081/travel/ | grep -F "¥24,862–40,772" && curl -fsSI "http://127.0.0.1:8081/travel/travel.css?v=7" && curl -fsSI "http://127.0.0.1:8081/travel/travel.js?v=5" && curl -fsSI "http://127.0.0.1:8081/travel/assets/og-travel.png?v=4"
```

Expected: all content checks succeed and assets return HTTP 200.

- [ ] **Step 7: Verify public output and cache freshness**

```bash
cd /home/shunlyu/work/website/homepage-travel-itinerary && curl -fsS https://shunlyu.com/travel/ | grep -F "三套完整行程" && curl -fsS https://shunlyu.com/travel/ | grep -F 'data-route-panel="route-b"' && curl -fsS https://shunlyu.com/travel/ | grep -F 'data-route-panel="route-c"' && curl -fsSI "https://shunlyu.com/travel/travel.css?v=7" && curl -fsSI "https://shunlyu.com/travel/travel.js?v=5" && curl -fsSI "https://shunlyu.com/travel/assets/og-travel.png?v=4"
```

Expected: HTTP 200, fresh asset URLs, and public HTML containing all three static panels.

Use Playwright on the public URLs
`https://shunlyu.com/travel/#route-a`,
`https://shunlyu.com/travel/#route-b`, and
`https://shunlyu.com/travel/#route-c`. For each URL, assert the matching route
panel is the only visible panel, the matching tab is selected, the comparison
is hidden, and the URL retains the canonical hash.

- [ ] **Step 8: Compare deployed content and asset checksums**

```bash
cd /home/shunlyu/work/website/homepage-travel-itinerary && checksum() { curl -fsS "$1" | sha256sum | cut -d' ' -f1; } && local_html="$(checksum http://127.0.0.1:8081/travel/)" && public_html="$(checksum https://shunlyu.com/travel/)" && local_css="$(checksum 'http://127.0.0.1:8081/travel/travel.css?v=7')" && public_css="$(checksum 'https://shunlyu.com/travel/travel.css?v=7')" && local_js="$(checksum 'http://127.0.0.1:8081/travel/travel.js?v=5')" && public_js="$(checksum 'https://shunlyu.com/travel/travel.js?v=5')" && local_og="$(checksum 'http://127.0.0.1:8081/travel/assets/og-travel.png?v=4')" && public_og="$(checksum 'https://shunlyu.com/travel/assets/og-travel.png?v=4')" && printf 'html %s %s\ncss  %s %s\njs   %s %s\nog   %s %s\n' "$local_html" "$public_html" "$local_css" "$public_css" "$local_js" "$public_js" "$local_og" "$public_og" && test "$local_html" = "$public_html" && test "$local_css" = "$public_css" && test "$local_js" = "$public_js" && test "$local_og" = "$public_og"
```

Expected: each local/public pair prints identical SHA-256 checksums and every
`test` returns success.

- [ ] **Step 9: Remove the temporary review ref**

```bash
cd /home/shunlyu/work/website/homepage-travel-itinerary && git update-ref -d refs/reviews/travel-itinerary && test "$(git rev-parse HEAD)" = "$(git -C /home/shunlyu/work/website/homepage rev-parse HEAD)"
```
