import sys
from pathlib import Path

OUTPUT_SVG = Path(__file__).resolve().parent.parent / "info-card.svg"

# System profile & tech specs
FIELDS = [
    ("OS", "Arch Linux x86_64"),
    ("Host", "B.Tech CSE (AI/ML) — 2nd Year"),
    ("Kernel", "Karman Singh @ Karmansingh09"),
    ("Uptime", "Curious, building &amp; shipping continuously"),
    ("Focus", "AI/ML • Web3 / Blockchain • Full-Stack • DevOps"),
    ("Languages", "C, Python, TypeScript, JavaScript, Java"),
    ("Frontend", "React, Next.js, Vite, Tailwind CSS"),
    ("Backend", "Node.js, Express, MongoDB"),
    ("Web3 / DLT", "Celo, Midnight Network, Stellar, Solidity"),
    ("Tools &amp; Env", "Git, GitHub, Docker, Linux, Neovim / VS Code"),
]

PROJECTS = [
    ("RoadEye / NetraFlow", "AI-powered ANPR &amp; urban traffic analytics"),
    ("Confidential P2P Lending", "Privacy-preserving credit desk on Midnight Network"),
    ("CeloAgent", "Autonomous on-chain agent spending &amp; policy controls"),
    ("MiniSwap", "Decentralized AMM &amp; liquidity pool protocol"),
]


def render_info_card():
    # Width matches contrib-heatmap.svg perfectly (840px)
    width = 840
    height = 360

    title = "karman@github: ~ (sysinfo --developer)"

    lines_svg = []

    # Command prompt line
    start_y = 56
    lines_svg.append(f'''
    <g class="term-line" style="animation-delay: 0.08s;">
      <text x="26" y="{start_y}" class="prompt-user">karman@github</text>
      <text x="116" y="{start_y}" class="prompt-sep">:</text>
      <text x="124" y="{start_y}" class="prompt-path">~</text>
      <text x="134" y="{start_y}" class="prompt-sep">$</text>
      <text x="146" y="{start_y}" class="cmd-text">neofetch --developer --verbose</text>
    </g>''')

    # Divider bar
    div_y = start_y + 13
    lines_svg.append(f'''
    <g class="term-line" style="animation-delay: 0.16s;">
      <line x1="26" y1="{div_y}" x2="{width - 26}" y2="{div_y}" stroke="#30363d" stroke-width="1" stroke-dasharray="3,3" />
    </g>''')

    # Column layout:
    # Left column: System specifications (x: 26 to 430)
    # Right column: Active deployments & quick telemetry (x: 460 to 814)
    # Vertical divider line at x: 445
    lines_svg.append(f'''
    <g class="term-line" style="animation-delay: 0.22s;">
      <line x1="440" y1="{div_y + 10}" x2="440" y2="{height - 40}" stroke="#21262d" stroke-width="1" />
    </g>''')

    # Render Left Column (System specs)
    current_y = div_y + 24
    line_height = 21.5
    delay = 0.22

    for key, val in FIELDS:
        delay += 0.05
        lines_svg.append(f'''
    <g class="term-line" style="animation-delay: {delay:.2f}s;">
      <text x="26" y="{current_y}" class="field-key">{key}</text>
      <text x="126" y="{current_y}" class="field-sep">&#10140;</text>
      <text x="142" y="{current_y}" class="field-val">{val}</text>
    </g>''')
        current_y += line_height

    # Render Right Column (Featured Projects & Telemetry)
    right_x = 460
    right_y = div_y + 24
    right_delay = 0.35

    # Section header: FEATURED_DEPLOYMENTS
    lines_svg.append(f'''
    <g class="term-line" style="animation-delay: {right_delay:.2f}s;">
      <text x="{right_x}" y="{right_y}" class="section-title">ACTIVE_DEPLOYMENTS</text>
      <line x1="{right_x + 155}" y1="{right_y - 4}" x2="{width - 26}" y2="{right_y - 4}" stroke="#21262d" stroke-width="1" />
    </g>''')

    proj_y = right_y + 22
    for pname, pdesc in PROJECTS:
        right_delay += 0.07
        lines_svg.append(f'''
    <g class="term-line" style="animation-delay: {right_delay:.2f}s;">
      <circle cx="{right_x + 6}" cy="{proj_y - 3.5}" r="3" fill="#39d353" />
      <text x="{right_x + 16}" y="{proj_y}" class="proj-name">{pname}</text>
      <text x="{right_x + 16}" y="{proj_y + 14}" class="proj-desc">{pdesc}</text>
    </g>''')
        proj_y += 33

    # Telemetry stat badges on right column bottom
    right_delay += 0.08
    badge_y = proj_y + 10
    lines_svg.append(f'''
    <g class="term-line" style="animation-delay: {right_delay:.2f}s;">
      <rect x="{right_x}" y="{badge_y}" width="168" height="24" rx="4" fill="#161b22" stroke="#30363d" stroke-width="0.8" />
      <circle cx="{right_x + 14}" cy="{badge_y + 12}" r="3.5" fill="#39d353" />
      <text x="{right_x + 26}" y="{badge_y + 16}" class="term-badge">STATUS: SHIP_READY</text>

      <rect x="{right_x + 180}" y="{badge_y}" width="170" height="24" rx="4" fill="#161b22" stroke="#30363d" stroke-width="0.8" />
      <circle cx="{right_x + 194}" cy="{badge_y + 12}" r="3.5" fill="#58a6ff" />
      <text x="{right_x + 206}" y="{badge_y + 16}" class="term-badge">NETWORK: WEB3_DLT</text>
    </g>''')

    # Color palette bar (neofetch style) at bottom
    delay += 0.1
    colors = ["#21262d", "#ff5f56", "#27c93f", "#ffbd2e", "#58a6ff", "#bc8cff", "#39c5cf", "#f0f6fc"]
    color_rects = []
    block_w = 22
    block_h = 9
    start_bx = 26
    by = height - 20
    for i, c in enumerate(colors):
        color_rects.append(f'<rect x="{start_bx + i * (block_w + 5)}" y="{by}" width="{block_w}" height="{block_h}" rx="2" fill="{c}" />')

    colors_markup = "".join(color_rects)
    lines_svg.append(f'''
    <g class="term-line" style="animation-delay: {delay:.2f}s;">
      {colors_markup}
      <!-- Blinking block cursor -->
      <rect x="{start_bx + len(colors) * (block_w + 5) + 10}" y="{by}" width="8" height="{block_h}" fill="#58a6ff" class="cursor" />
      <text x="{width - 26}" y="{by + 8}" text-anchor="end" class="footer-text">SHELL: <tspan class="footer-accent">ZSH</tspan> | UTF-8</text>
    </g>''')

    body_content = "\n".join(lines_svg)

    svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="auto" preserveAspectRatio="xMidYMid meet">
  <defs>
    <linearGradient id="cardBg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0d1117" />
      <stop offset="100%" stop-color="#0a0d12" />
    </linearGradient>
    <linearGradient id="cardHeader" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#161b22" />
      <stop offset="100%" stop-color="#0d1117" />
    </linearGradient>
  </defs>

  <style>
    .card-border {{
      fill: url(#cardBg);
      stroke: #30363d;
      stroke-width: 1;
    }}
    .card-header {{
      fill: url(#cardHeader);
      stroke: #30363d;
      stroke-width: 0.5;
    }}
    .btn-red {{ fill: #ff5f56; }}
    .btn-yellow {{ fill: #ffbd2e; }}
    .btn-green {{ fill: #27c93f; }}

    .card-title {{
      font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, "Liberation Mono", monospace;
      font-size: 11px;
      font-weight: 600;
      fill: #8b949e;
      letter-spacing: 0.5px;
    }}

    .prompt-user {{
      font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, "Liberation Mono", monospace;
      font-size: 11.5px;
      font-weight: 700;
      fill: #39d353;
    }}
    .prompt-sep {{
      font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, "Liberation Mono", monospace;
      font-size: 11.5px;
      fill: #8b949e;
    }}
    .prompt-path {{
      font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, "Liberation Mono", monospace;
      font-size: 11.5px;
      font-weight: 700;
      fill: #58a6ff;
    }}
    .cmd-text {{
      font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, "Liberation Mono", monospace;
      font-size: 11.5px;
      fill: #f0f6fc;
    }}

    .field-key {{
      font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, "Liberation Mono", monospace;
      font-size: 11px;
      font-weight: 600;
      fill: #58a6ff;
    }}
    .field-sep {{
      font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, "Liberation Mono", monospace;
      font-size: 10px;
      fill: #6e7681;
    }}
    .field-val {{
      font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, "Liberation Mono", monospace;
      font-size: 11px;
      fill: #c9d1d9;
    }}

    .section-title {{
      font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, "Liberation Mono", monospace;
      font-size: 10.5px;
      font-weight: 700;
      letter-spacing: 1px;
      fill: #e3b341;
    }}
    .proj-name {{
      font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, "Liberation Mono", monospace;
      font-size: 11px;
      font-weight: 600;
      fill: #e6edf3;
    }}
    .proj-desc {{
      font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, "Liberation Mono", monospace;
      font-size: 10px;
      fill: #8b949e;
    }}

    .term-badge {{
      font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, "Liberation Mono", monospace;
      font-size: 9.5px;
      font-weight: 600;
      fill: #c9d1d9;
      letter-spacing: 0.4px;
    }}

    .footer-text {{
      font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, "Liberation Mono", monospace;
      font-size: 9.5px;
      fill: #6e7681;
    }}
    .footer-accent {{
      font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, "Liberation Mono", monospace;
      font-size: 9.5px;
      font-weight: 600;
      fill: #39d353;
    }}

    /* Sequential fade and slight slide-in */
    @keyframes lineFadeIn {{
      0% {{
        opacity: 0;
        transform: translateY(4px);
      }}
      100% {{
        opacity: 1;
        transform: translateY(0);
      }}
    }}

    .term-line {{
      opacity: 0;
      animation-name: lineFadeIn;
      animation-duration: 0.35s;
      animation-timing-function: cubic-bezier(0.16, 1, 0.3, 1);
      animation-fill-mode: forwards;
    }}

    /* Subtle cursor blink */
    @keyframes cursorBlink {{
      0%, 45% {{ opacity: 1; }}
      55%, 100% {{ opacity: 0.2; }}
    }}
    .cursor {{
      animation: cursorBlink 1.1s infinite;
    }}
  </style>

  <!-- Container Box -->
  <rect x="1" y="1" width="{width - 2}" height="{height - 2}" rx="8" class="card-border" />

  <!-- Terminal Header Bar -->
  <path d="M 1 9 A 8 8 0 0 1 9 1 L {width - 9} 1 A 8 8 0 0 1 {width - 1} 9 L {width - 1} 30 L 1 30 Z" class="card-header" />

  <!-- Window Controls -->
  <circle cx="16" cy="15" r="4.5" class="btn-red" />
  <circle cx="30" cy="15" r="4.5" class="btn-yellow" />
  <circle cx="44" cy="15" r="4.5" class="btn-green" />

  <!-- Window Title -->
  <text x="62" y="19" class="card-title">{title}</text>

  <!-- Terminal Body Lines -->
{body_content}
</svg>
'''
    OUTPUT_SVG.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_SVG, "w", encoding="utf-8") as f:
        f.write(svg_content.strip() + "\n")
    print(f"[✓] Successfully generated {OUTPUT_SVG} ({width}x{height})")


if __name__ == "__main__":
    render_info_card()
