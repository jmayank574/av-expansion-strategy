"""Generate reports/deck.pptx (7 slides) and reports/charts/*.png (200 dpi) from data/output/metros_scored.json."""
import pathlib, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import plan

CH = HERE / "charts"
CH.mkdir(exist_ok=True)
ACCENT, INK, MUTED, LINE, PANEL = "#1d4ed8", "#111827", "#6b7280", "#e5e7eb", "#f8fafc"
rgb = lambda h: RGBColor.from_string(h.lstrip("#").upper())
DPI = 200

p = plan.build()
d, by, cand = p["d"], p["by"], p["cand"]
meta = d["meta"]
plan.set_weights(meta)
vegas = next(m for m in d["metros"] if m["benchmark"])
pct = lambda x: f"{x * 100:.0f}%"
plt.rcParams.update({"font.family": "DejaVu Sans", "axes.edgecolor": MUTED, "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": MUTED})


def place_labels(fig, ax, labelled, bubbles):
    """Greedy label placement on the rendered figure: for each label try right, left, above, below and the diagonals, and keep the first spot
    inside the axes that overlaps no earlier label and no bubble (own bubble excepted). labelled: (text, x, y, marker_area, wave)."""
    fig.canvas.draw()
    rend = fig.canvas.get_renderer()
    px = fig.dpi / 72
    inside = ax.get_window_extent()
    pts = [(*ax.transData.transform((x, y)), (s / 3.14159) ** 0.5 * px) for x, y, s in bubbles]       # centre (px) and radius (px)
    placed = []
    CANDS = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    for text, x, y, s, wv in sorted(labelled, key=lambda r: (r[4] == 0, r[4])):                      # wave 1 first, benchmark last
        cx, cy = ax.transData.transform((x, y))
        r_pt = (s / 3.14159) ** 0.5
        best = None
        for sx, sy in CANDS:
            off = r_pt + 2.5
            ann = ax.annotate(text, (x, y), xytext=(sx * off, sy * off), textcoords="offset points", fontsize=9.5, color=INK,
                              ha="left" if sx > 0 else "right" if sx < 0 else "center", va="center" if sy == 0 else "bottom" if sy > 0 else "top",
                              fontweight="bold" if wv == 1 else "normal")
            bb = ann.get_window_extent(rend).expanded(1.04, 1.12)
            clash = (not (inside.x0 <= bb.x0 and bb.x1 <= inside.x1 and inside.y0 <= bb.y0 and bb.y1 <= inside.y1)
                     or any(bb.overlaps(o) for o in placed)
                     or any((abs(bx - cx) > 1 or abs(by - cy) > 1) and bb.x0 - br < bx < bb.x1 + br and bb.y0 - br < by < bb.y1 + br for bx, by, br in pts))
            if not clash:
                best = ann
                break
            ann.remove()
        if best is None:                                  # no clean spot: fall back to the right-hand side
            best = ax.annotate(text, (x, y), xytext=(r_pt + 2.5, 0), textcoords="offset points", fontsize=9.5, color=INK, va="center")
        placed.append(best.get_window_extent(rend).expanded(1.04, 1.12))


# ---------------------------------------------------------------- charts
def chart_quadrant():
    """Every wave 1-3 metro and Las Vegas is labeled; marker style shows the wave."""
    from matplotlib.lines import Line2D
    wave = {m["metro"]: i for i, ws in enumerate((p["w1"], p["w2"], p["w3"]), 1) for m in ws}
    fig, ax = plt.subplots(figsize=(11, 5.4), dpi=DPI)
    mx, my = p["med_ease"], p["med_opp"]
    ax.axvline(mx, color="#9ca3af", ls=(0, (5, 4)), lw=1)
    ax.axhline(my, color="#9ca3af", ls=(0, (5, 4)), lw=1)
    sty = {1: dict(facecolor=ACCENT, edgecolor="white", alpha=1.0), 2: dict(facecolor=ACCENT, edgecolor="white", alpha=0.5),
           3: dict(facecolor="white", edgecolor=ACCENT, alpha=1.0), 0: dict(facecolor="#9ca3af", edgecolor="white", alpha=0.35)}
    for m in cand:
        w = wave.get(m["metro"], 0)
        ax.scatter(m["ease_of_entry"], m["opportunity"], s=60 + 260 * m["raw"]["crowding"], linewidth=1.6 if w == 3 else 1.2, zorder=3, **sty[w])
    ax.scatter(vegas["ease_of_entry"], vegas["opportunity"], marker="D", s=110, color=INK, zorder=4)
    ax.set_xlim(ax.get_xlim()[0] - 2, ax.get_xlim()[1] + 1); ax.set_ylim(ax.get_ylim()[0] - 4, ax.get_ylim()[1] + 9)
    x0, x1 = ax.get_xlim(); y0, y1 = ax.get_ylim()
    kw = dict(fontsize=10, fontweight="bold", alpha=0.9)
    ax.text(x0 + 0.5, y1 - 1.5, "BUILD CASE", color=MUTED, va="top", **kw)
    ax.text(x1 - 0.5, y1 - 1.5, "LAUNCH NEXT", color=ACCENT, va="top", ha="right", **kw)
    ax.text(x0 + 0.5, y0 + 1.5, "DEPRIORITIZE", color=MUTED, va="bottom", **kw)
    ax.text(x1 - 0.5, y0 + 1.5, "OPPORTUNISTIC", color=MUTED, va="bottom", ha="right", **kw)
    ax.set_xlabel("Ease of entry (regulation, weather, competition, charging)  →")
    ax.set_ylabel("Opportunity (demand)  →")
    ax.grid(color="#eef0f3", lw=0.8, zorder=0)
    for s in ("top", "right"): ax.spines[s].set_visible(False)
    handles = [Line2D([], [], marker="o", ls="", markersize=9, markerfacecolor=ACCENT, markeredgecolor="white", label="Wave 1"),
               Line2D([], [], marker="o", ls="", markersize=9, markerfacecolor=ACCENT, alpha=0.5, markeredgecolor="white", label="Wave 2"),
               Line2D([], [], marker="o", ls="", markersize=9, markerfacecolor="white", markeredgecolor=ACCENT, markeredgewidth=1.6, label="Wave 3"),
               Line2D([], [], marker="o", ls="", markersize=9, markerfacecolor="#9ca3af", alpha=0.5, markeredgecolor="white", label="Not in a wave")]
    ax.legend(handles=handles, loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=4, frameon=False, fontsize=9.5, labelcolor=INK)
    ax.text(0.99, -0.16, "Bubble size = competitor crowding. Dashed lines = medians of the 25 candidates.", transform=ax.transAxes, ha="right", fontsize=8.5, color=MUTED)
    fig.tight_layout()
    place_labels(fig, ax, [(m["metro"], m["ease_of_entry"], m["opportunity"], 60 + 260 * m["raw"]["crowding"], wave[m["metro"]]) for m in cand if m["metro"] in wave]
                 + [("Las Vegas (benchmark)", vegas["ease_of_entry"], vegas["opportunity"], 110, 0)],
                 [(m["ease_of_entry"], m["opportunity"], 60 + 260 * m["raw"]["crowding"]) for m in cand] + [(vegas["ease_of_entry"], vegas["opportunity"], 110)])
    f = CH / "quadrant.png"; fig.savefig(f, dpi=DPI); plt.close(fig)
    return f


def pool(m, case="base"):
    """Annual revenue pool in $M = fleet x annual revenue per vehicle."""
    u = m["unit_economics"][case]
    return u["fleet_vehicles"] * u["revenue_per_vehicle"] / 1e6


def chart_unit_econ(top):
    names = [m["metro"] for m in top]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.4), dpi=DPI)
    y = list(range(len(top)))
    for ax, fn, title, fmt in ((a1, plan.fleet, "Fleet needed, vehicles", "{:,.0f}"), (a2, pool, "Annual revenue pool, $M", "${:,.0f}M")):
        base = [fn(m) for m in top]; lo = [fn(m, "low") for m in top]; hi = [fn(m, "high") for m in top]
        ax.barh(y, base, color=ACCENT, height=0.5, zorder=3)
        ax.errorbar(base, y, xerr=[[b - l for b, l in zip(base, lo)], [h - b for b, h in zip(base, hi)]], fmt="none", ecolor=MUTED, elinewidth=1.2, capsize=4, zorder=4)
        for i in y: ax.text(hi[i] + max(hi) * 0.02, i, fmt.format(base[i]), va="center", fontsize=10, color=INK)
        ax.set_xlim(0, max(hi) * 1.18)
        ax.set_title(f"{title} (base; whiskers = low to high case)", fontsize=10.5, color=INK, loc="left")
        ax.grid(axis="x", color="#eef0f3", lw=0.8, zorder=0)
        for s in ("top", "right"): ax.spines[s].set_visible(False)
        ax.invert_yaxis()
    a1.set_yticks(y); a1.set_yticklabels(names, fontsize=10.5, color=INK); a2.set_yticks(y); a2.set_yticklabels([])
    fig.tight_layout()
    f = CH / "unit_economics.png"; fig.savefig(f, dpi=DPI); plt.close(fig)
    return f


# ---------------------------------------------------------------- slide helpers
prs = Presentation()
prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
BLANK = prs.slide_layouts[6]


def text(slide, x, y, w, h, s, size=18, bold=False, color=INK, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame; tf.word_wrap = True; tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = Inches(0.05)
    lines = s if isinstance(s, list) else [s]
    for i, ln in enumerate(lines):
        para = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        para.alignment = align
        r = para.add_run(); r.text = ln
        r.font.size = Pt(size); r.font.bold = bold; r.font.color.rgb = rgb(color); r.font.name = "Calibri"
    return tb


def rich(slide, x, y, w, h, items):
    """One text box, one paragraph per (text, size, bold, color) item."""
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame; tf.word_wrap = True
    tf.margin_left = tf.margin_right = Inches(0.05)
    for i, (s_, size, bold, color) in enumerate(items):
        para = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        para.space_before = Pt(5 if size >= 20 and i else 0)
        r = para.add_run(); r.text = s_
        r.font.size = Pt(size); r.font.bold = bold; r.font.color.rgb = rgb(color); r.font.name = "Calibri"
    return tb


def box(slide, x, y, w, h, fill=PANEL, line=LINE):
    sh = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    sh.adjustments[0] = 0.04
    sh.fill.solid(); sh.fill.fore_color.rgb = rgb(fill)
    sh.line.color.rgb = rgb(line); sh.line.width = Pt(0.75)
    sh.shadow.inherit = False
    return sh


def new_slide(title, n):
    s = prs.slides.add_slide(BLANK)
    bar = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, Inches(0.12))
    bar.fill.solid(); bar.fill.fore_color.rgb = rgb(ACCENT); bar.line.fill.background()
    text(s, 0.6, 0.35, 12.1, 1.3, title, size=30, bold=True)
    text(s, 0.6, 7.0, 11.4, 0.3, plan.sources_line(meta), size=10, color=MUTED)
    text(s, 12.2, 7.0, 0.6, 0.3, str(n), size=10, color=MUTED, align=PP_ALIGN.RIGHT)
    return s


# ---------------------------------------------------------------- slide 1
s = prs.slides.add_slide(BLANK)
bg = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
bg.fill.solid(); bg.fill.fore_color.rgb = rgb(ACCENT); bg.line.fill.background()
text(s, 0.8, 1.7, 11.7, 1.5, "Where should the operator launch after Las Vegas?", size=44, bold=True, color="#ffffff")
text(s, 0.8, 3.7, 11.5, 1.6, plan.one_line_answer(p), size=26, color="#dbe6fb")
text(s, 0.8, 6.4, 11, 0.5, f"Strategy team readout  |  25 US metros scored  |  data as of {meta['data_as_of']}", size=14, color="#dbe6fb")

# ---------------------------------------------------------------- slide 2
s = new_slide("Five criteria decide where a robotaxi launch works", 2)
W = meta["weights"]["scenarios"]["balanced"]
CARDS = [("demand", "Market demand", "Population, density, ride-hail use, no-car households, airport traffic"),
         ("operating", "Operating conditions", "Rain, snow and extreme-heat days"),
         ("regulatory", "Regulatory readiness", "State AV rules (tier 0-3) and a new operator's path to paid service"),
         ("competition", "Competitive intensity", "Who already operates or has announced"),
         ("charging", "Charging cost", "Commercial electricity price")]
for i, (k, name, sub) in enumerate(CARDS):
    x = 0.6 + i * 2.45
    box(s, x, 2.1, 2.3, 3.6)
    text(s, x + 0.1, 2.25, 2.1, 0.9, f"{W[k]}", size=44, bold=True, color=ACCENT)
    text(s, x + 0.1, 3.15, 2.1, 0.3, "weight, balanced case", size=10, color=MUTED)
    text(s, x + 0.1, 3.6, 2.1, 0.7, name, size=18, bold=True)
    text(s, x + 0.1, 4.4, 2.1, 1.2, sub, size=12, color=MUTED)
text(s, 0.6, 5.95, 12.1, 0.8, ["25 candidate metros, each scored 0-100. Metrics are percentile-ranked, except competitor crowding, which is min-max scaled.", "Las Vegas is scored as a benchmark, not ranked."], size=14, color=MUTED)

# ---------------------------------------------------------------- slide 3
elig = sorted([m for m in cand if m["regulation"]["tier"] >= 2], key=lambda m: m["ranks"]["balanced"])[:len(p["w1"])]
if {m["metro"] for m in elig} == {m["metro"] for m in p["w1"]}:      # only claim "top-scoring" when it is true
    title3 = f"{plan.names(p['w1'])} are the top-scoring metros where driverless service is already allowed"
else:
    title3 = f"Enter {plan.names(p['w1'])} first"
s = new_slide(title3, 3)
s.shapes.add_picture(str(chart_quadrant()), Inches(0.6), Inches(1.65), width=Inches(12.1))

# ---------------------------------------------------------------- slide 4
s = new_slide("Launch in three waves, gated by regulation and proof", 4)
cols = [("Wave 1", (f"Start now: {len(plan.wave1_split(p)[0])} launch, {len(plan.wave1_split(p)[1])} start permits" if plan.wave1_split(p)[1] else "Start now"), p["w1"], "Tier 2+ rules, top-5 in at least half of weight draws"),
        ("Wave 2", "After wave 1 proves the playbook", p["w2"], "Tier 2+ rules, top 10; validate weather"),
        ("Wave 3", "When the law changes", p["w3"], "Top-10 demand, driverless service not yet allowed")]
for i, (wn, when, ms, rule) in enumerate(cols):
    x = 0.6 + i * 4.1
    box(s, x, 1.9, 3.9, 4.6, fill="#ffffff" if i else "#eef3ff", line=ACCENT if i == 0 else LINE)
    text(s, x + 0.15, 2.0, 3.6, 0.5, wn, size=24, bold=True, color=ACCENT)
    text(s, x + 0.15, 2.6, 3.6, 0.4, when, size=14, color=MUTED)
    if i == 0:
        # wave 1 is not one launch date: metros in slow-permit states start permits now, paid service follows
        first, slow = plan.wave1_split(p)
        items = []
        for m in first:
            items += [(m["metro"], 20, True, INK), ("launches first", 11, False, MUTED)]
        for m in slow:
            items += [(m["metro"], 20, True, INK), (f"{plan.STATE_NAMES.get(m['state'], m['state'])}: permits now, paid service after", 11, False, MUTED)]
            if m["confidence"] < 0.6:
                items += [(f"only just clears the 50% gate ({m['confidence'] * 100:.0f}%)", 11, False, MUTED)]
        rich(s, x + 0.15, 3.05, 3.6, 2.7, items)
    else:
        text(s, x + 0.15, 3.15, 3.6, 2.2, [m["metro"] for m in ms], size=22, bold=True)
    text(s, x + 0.15, 5.8, 3.6, 0.65, rule, size=12, color=MUTED)
text(s, 0.6, 6.6, 12, 0.35, "Timing is indicative: sequence follows evidence gates, not calendar dates", size=11, color=MUTED)

# ---------------------------------------------------------------- slide 5
w1m = sorted(p["w1"], key=lambda m: m["ranks"]["balanced"])          # wave 1 only, in rank order
fl = [plan.fleet(m) for m in w1m]
pl = [pool(m) for m in w1m]
pays = [m["unit_economics"]["base"]["payback_years"] for m in w1m]
cap, fare = meta["assumptions"]["capture_share"]["value"], meta["assumptions"]["avg_fare_usd"]["value"]
top = w1m[0]
small = (f", which is why {top['metro']}'s pool is small despite ranking #{top['ranks']['balanced']}" if pool(top) == min(pl) else "")
s = new_slide(f"Wave 1 needs {min(fl):,.0f}-{max(fl):,.0f} vehicles per metro for a ${min(pl):,.0f}M-${max(pl):,.0f}M annual revenue pool", 5)
s.shapes.add_picture(str(chart_unit_econ(w1m)), Inches(1.15), Inches(1.7), width=Inches(11.0))
text(s, 0.6, 6.2, 12.1, 0.75, f"Wave 1 metros, base case: {cap * 100:.0f}% capture of ride-hail trips, ${fare:.0f} fare. Demand and revenue are for the principal-city launch area, not the whole metro{small}. "
     f"Payback is assumption-driven: about {min(pays):.1f}-{max(pays):.1f} years in every metro because fare, utilization and cost per mile are national assumptions (only the power price varies).", size=11, color=MUTED)
s.notes_slide.notes_text_frame.text = "Chart metros (wave 1 only): " + ", ".join(m["metro"] for m in w1m)

# ---------------------------------------------------------------- slide 6
crowded = [m for m in p["w1"] if m["raw"]["crowding"] >= 1.0]
s = new_slide("Regulation, weather and crowding are the three risks to manage", 6)
n_low = sum(1 for m in cand if m["ranks"]["balanced"] <= 10 and m["regulation"]["tier"] <= 1)
slow_open = sorted({m["state"] for m in p["w1"] + p["w2"] if m["regulation"]["tier"] >= 2 and m["regulation"]["new_entrant_path"] == "slow"})
rows = [("Regulation", f"{n_low} of the top 10 are in Tier 0-1 states; {plan.names(slow_open)} permits are slow for a new entrant", "Engage regulators early; file in slow-permit states during wave 1; hold wave 3 until the law changes"),
        ("Weather", plan.weather_evidence(p), plan.weather_mitigation(p)),
        ("Competition", f"{plan.names(crowded)} already have operators (crowding {min(m['raw']['crowding'] for m in crowded):.1f}-{max(m['raw']['crowding'] for m in crowded):.1f})", f"Enter with a service or cost edge. {plan.fewest_operators_note(p)}")]
text(s, 0.6, 1.85, 2.4, 0.4, "RISK", size=12, bold=True, color=MUTED)
text(s, 3.2, 1.85, 4.6, 0.4, "EVIDENCE", size=12, bold=True, color=MUTED)
text(s, 8.2, 1.85, 4.5, 0.4, "MITIGATION", size=12, bold=True, color=MUTED)
for i, (r, e, mtg) in enumerate(rows):
    y = 2.35 + i * 1.45
    box(s, 0.6, y, 12.1, 1.3)
    text(s, 0.75, y + 0.1, 2.3, 1.1, r, size=22, bold=True, color=ACCENT, anchor=MSO_ANCHOR.MIDDLE)
    text(s, 3.2, y + 0.1, 4.8, 1.1, e, size=15, anchor=MSO_ANCHOR.MIDDLE)
    text(s, 8.2, y + 0.1, 4.4, 1.1, mtg, size=15, anchor=MSO_ANCHOR.MIDDLE)

# ---------------------------------------------------------------- slide 7
s = new_slide("Appendix: methodology and sources", 7)
left = ["Percentile rank of each metric across 25 metros, except competitor crowding (min-max scaled)",
        "Pillar score = weighted mean of its sub-scores",
        "Total = weighted mean of five pillars",
        "Opportunity = demand; ease = other four pillars",
        "Monte Carlo: 10,000 weight draws (Dirichlet, seed 42)",
        "Demand: two anchors, Chicago and NYC, calendar 2025",
        "Unit economics: labeled assumptions, benchmarked to public references (Obi fares, Morgan Stanley vehicle cost, AAA operating cost)"]
v = meta["vintages"]
right = [f"Census ACS {v['acs']}", f"FAA {v['faa']}", "NOAA GHCN-Daily airport stations, 2016-2025", "NHTSA SGO ADS reports to Sep 2026 (activity only)",
         v["eia"].split(" (")[0].replace("August 2026 YTD", "EIA commercial price, Jan-Aug 2026"), f"Researched seed files: AV rules, new-entrant paths, competitors (as of {meta['data_as_of']})",
         "Chicago TNP and NYC TLC trip counts"]
text(s, 0.6, 1.75, 5.9, 0.4, "METHOD", size=12, bold=True, color=MUTED)
text(s, 7.0, 1.75, 5.7, 0.4, "SOURCES", size=12, bold=True, color=MUTED)
text(s, 0.6, 2.2, 6.0, 4.5, ["•  " + t for t in left], size=16)
text(s, 7.0, 2.2, 5.7, 4.5, ["•  " + t for t in right], size=16)
text(s, 0.6, 6.05, 12.1, 0.5, f"Inputs validated against Census estimates, NYC TLC and Chicago trip data; all competitor and regulation sources re-checked {meta['data_as_of']} (docs/validation.md)", size=13, color=INK)
text(s, 0.6, 6.55, 12, 0.35, "NHTSA reports have no mileage: never used as crash rates. Full method in the methodology note", size=11, color=MUTED)

out = HERE / "deck.pptx"
prs.save(out)
print(f"wrote {out} with {len(prs.slides)} slides")
