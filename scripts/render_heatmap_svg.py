import json
import sys
from pathlib import Path
from datetime import datetime

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "contributions.json"
OUTPUT_SVG = Path(__file__).resolve().parent.parent / "contrib-heatmap.svg"

# Palette: Dark Terminal GitHub aesthetic
# 0: empty, 1: low, 2: medium, 3: high, 4: very high
COLORS = [
    "#161b22",  # Level 0 (bg dark)
    "#0e4429",  # Level 1
    "#006d32",  # Level 2
    "#26a641",  # Level 3
    "#39d353",  # Level 4
]

BORDER_COLORS = [
    "#21262d",
    "#0e4429",
    "#006d32",
    "#26a641",
    "#39d353",
]


def load_contributions():
    if not DATA_FILE.exists():
        print(f"[!] Warning: {DATA_FILE} not found. Using placeholder data.")
        return {"stats": {"total_contributions": 0, "current_streak": 0, "longest_streak": 0}, "days": []}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def render_svg():
    data = load_contributions()
    days = data.get("days", [])
    stats = data.get("stats", {})
    total_contribs = stats.get("total_contributions", 0)
    current_streak = stats.get("current_streak", 0)
    longest_streak = stats.get("longest_streak", 0)
    
    # We want ~53 weeks of 7 days (371 days max)
    # Take the last 371 days if we have more
    if len(days) > 371:
        days = days[-371:]
    elif not days:
        # Generate dummy 53 weeks
        days = [{"date": "2026-01-01", "count": 0, "level": 0} for _ in range(371)]
        
    # Group into weeks (columns). Each column has up to 7 days (Sunday=0 to Saturday=6).
    # Days from GitHub contribution calendar start on Sunday.
    weeks = []
    current_week = []
    for d in days:
        current_week.append(d)
        if len(current_week) == 7:
            weeks.append(current_week)
            current_week = []
    if current_week:
        weeks.append(current_week)

    # Geometry settings
    cell_size = 11
    cell_gap = 3.5
    step = cell_size + cell_gap
    corner_radius = 2.5
    
    margin_left = 32
    margin_top = 88
    
    # Calculate months and their week positions
    month_labels = []
    prev_month = None
    for w_idx, week in enumerate(weeks):
        first_day_of_week = week[0]["date"]
        # YYYY-MM-DD
        m_str = first_day_of_week[5:7]
        if m_str != prev_month:
            # Format month name
            m_num = int(m_str)
            m_name = datetime(2000, m_num, 1).strftime("%b")
            month_labels.append((w_idx, m_name))
            prev_month = m_str

    num_weeks = len(weeks)
    grid_width = num_weeks * step
    width = 840
    height = 230
    
    # Generate cells SVG with progressive diagonal reveal animation
    # Diagonal factor = (col + row) / (num_weeks + 7)
    # Base duration 0.3s, staggered delay
    cells_svg = []
    max_diag = num_weeks + 7
    total_anim_duration = 1.2  # Total wave duration
    
    for c_idx, week in enumerate(weeks):
        x = margin_left + c_idx * step
        for r_idx, day in enumerate(week):
            y = margin_top + r_idx * step
            lvl = min(max(day.get("level", 0), 0), 4)
            color = COLORS[lvl]
            border = BORDER_COLORS[lvl]
            count = day.get("count", 0)
            date_str = day.get("date", "")
            
            # Diagonal index
            diag_idx = c_idx + r_idx
            delay = round((diag_idx / max_diag) * total_anim_duration, 3)
            
            tooltip = f"{count} contributions on {date_str}"
            
            cell_element = f'''    <rect class="cell" x="{x:.1f}" y="{y:.1f}" width="{cell_size}" height="{cell_size}" rx="{corner_radius}" ry="{corner_radius}" fill="{color}" stroke="{border}" stroke-width="0.5" style="animation-delay: {delay}s;">
      <title>{tooltip}</title>
    </rect>'''
            cells_svg.append(cell_element)

    cells_markup = "\n".join(cells_svg)
    
    # Month labels
    month_svg = []
    for w_idx, m_name in month_labels:
        # Don't place too close to end
        if w_idx * step < grid_width - 25:
            mx = margin_left + w_idx * step
            my = margin_top - 10
            month_svg.append(f'    <text x="{mx:.1f}" y="{my:.1f}" class="lbl-month">{m_name}</text>')
    months_markup = "\n".join(month_svg)

    # Day labels (Mon, Wed, Fri) -> rows 1, 3, 5
    day_labels = [
        (1, "Mon"),
        (3, "Wed"),
        (5, "Fri")
    ]
    days_markup = "\n".join([
        f'    <text x="{margin_left - 8}" y="{margin_top + r * step + 8.5}" text-anchor="end" class="lbl-day">{lbl}</text>'
        for r, lbl in day_labels
    ])
    
    # Legend at bottom right
    legend_x = margin_left + grid_width - 5 * step - 35
    legend_y = margin_top + 7 * step + 16
    legend_cells = []
    for l_idx, col in enumerate(COLORS):
        lx = legend_x + 32 + l_idx * (cell_size + 3)
        legend_cells.append(
            f'<rect x="{lx:.1f}" y="{legend_y - 8.5:.1f}" width="{cell_size}" height="{cell_size}" rx="{corner_radius}" fill="{col}" stroke="{BORDER_COLORS[l_idx]}" stroke-width="0.5" />'
        )
    legend_cells_markup = "".join(legend_cells)

    svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="auto" preserveAspectRatio="xMidYMid meet">
  <defs>
    <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0d1117" />
      <stop offset="100%" stop-color="#0a0d12" />
    </linearGradient>
    <linearGradient id="headerGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#161b22" />
      <stop offset="100%" stop-color="#0d1117" />
    </linearGradient>
  </defs>

  <style>
    .terminal-bg {{
      fill: url(#bgGrad);
      stroke: #30363d;
      stroke-width: 1;
    }}
    .terminal-header {{
      fill: url(#headerGrad);
      stroke: #30363d;
      stroke-width: 0.5;
    }}
    .btn-red {{ fill: #ff5f56; }}
    .btn-yellow {{ fill: #ffbd2e; }}
    .btn-green {{ fill: #27c93f; }}
    
    .term-title {{
      font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, "Liberation Mono", monospace;
      font-size: 11px;
      font-weight: 600;
      fill: #8b949e;
      letter-spacing: 0.5px;
    }}
    
    .stat-label {{
      font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, "Liberation Mono", monospace;
      font-size: 10px;
      fill: #8b949e;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }}
    .stat-val {{
      font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, "Liberation Mono", monospace;
      font-size: 13px;
      font-weight: 700;
      fill: #39d353;
    }}
    .stat-val-muted {{
      font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, "Liberation Mono", monospace;
      font-size: 13px;
      font-weight: 700;
      fill: #58a6ff;
    }}

    .lbl-month, .lbl-day, .lbl-legend {{
      font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, "Liberation Mono", monospace;
      font-size: 9px;
      fill: #6e7681;
    }}

    /* Diagonal reveal animation */
    @keyframes cellFadeIn {{
      0% {{
        opacity: 0;
        transform: scale(0.4);
      }}
      70% {{
        transform: scale(1.15);
      }}
      100% {{
        opacity: 1;
        transform: scale(1);
      }}
    }}

    .cell {{
      opacity: 0;
      transform-origin: center;
      animation-name: cellFadeIn;
      animation-duration: 0.4s;
      animation-timing-function: cubic-bezier(0.16, 1, 0.3, 1);
      animation-fill-mode: forwards;
    }}
  </style>

  <!-- Container Box -->
  <rect x="1" y="1" width="{width - 2}" height="{height - 2}" rx="8" class="terminal-bg" />

  <!-- Terminal Header Bar -->
  <path d="M 1 9 A 8 8 0 0 1 9 1 L {width - 9} 1 A 8 8 0 0 1 {width - 1} 9 L {width - 1} 30 L 1 30 Z" class="terminal-header" />
  
  <!-- Window Controls -->
  <circle cx="16" cy="15" r="4.5" class="btn-red" />
  <circle cx="30" cy="15" r="4.5" class="btn-yellow" />
  <circle cx="44" cy="15" r="4.5" class="btn-green" />

  <!-- Window Title -->
  <text x="64" y="19" class="term-title">karman@github: ~/contributions (live telemetry)</text>

  <!-- Quick Metrics / Stats Bar -->
  <g id="metrics">
    <!-- Total Contributions -->
    <text x="{margin_left}" y="52" class="stat-label">Contributions</text>
    <text x="{margin_left}" y="68" class="stat-val">{total_contribs}</text>
    <text x="{margin_left + 45}" y="68" class="term-title" font-size="10px">in the last year</text>

    <!-- Current Streak -->
    <text x="{margin_left + 230}" y="52" class="stat-label">Current Streak</text>
    <text x="{margin_left + 230}" y="68" class="stat-val-muted">{current_streak} <tspan font-size="10px" font-weight="normal" fill="#8b949e">days</tspan></text>

    <!-- Longest Streak -->
    <text x="{margin_left + 380}" y="52" class="stat-label">Longest Streak</text>
    <text x="{margin_left + 380}" y="68" class="stat-val-muted">{longest_streak} <tspan font-size="10px" font-weight="normal" fill="#8b949e">days</tspan></text>

    <!-- Status badge -->
    <rect x="{width - 145}" y="48" width="115" height="22" rx="4" fill="#161b22" stroke="#30363d" stroke-width="0.8" />
    <circle cx="{width - 133}" cy="59" r="3.5" fill="#39d353" />
    <text x="{width - 122}" y="63" class="term-title" font-size="9px" fill="#c9d1d9">TELEMETRY: OK</text>
  </g>

  <!-- Month Labels -->
  <g id="month-labels">
{months_markup}
  </g>

  <!-- Day Labels -->
  <g id="day-labels">
{days_markup}
  </g>

  <!-- Heatmap Grid -->
  <g id="cells-grid">
{cells_markup}
  </g>

  <!-- Legend -->
  <g id="legend">
    <text x="{legend_x:.1f}" y="{legend_y:.1f}" class="lbl-legend">Less</text>
    {legend_cells_markup}
    <text x="{legend_x + 32 + 5 * (cell_size + 3) + 4:.1f}" y="{legend_y:.1f}" class="lbl-legend">More</text>
  </g>
</svg>
'''
    OUTPUT_SVG.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_SVG, "w", encoding="utf-8") as f:
        f.write(svg_content.strip() + "\n")
    print(f"[✓] Successfully generated {OUTPUT_SVG} ({width}x{height})")


if __name__ == "__main__":
    render_svg()
