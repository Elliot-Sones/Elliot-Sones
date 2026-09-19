#!/usr/bin/env python3
"""Generate assets/tech-stack.svg: a seamless scrolling strip of devicon logos.

GitHub strips CSS from README markdown, so the animation has to live inside the
SVG itself: a <style> block within the SVG survives, which is how readme-typing-svg
and the contribution-snake animate on profile pages. Icons are inlined as base64
data URIs because external references are blocked inside an <img>-loaded SVG.

Usage: python3 scripts/gen_tech_stack.py
"""
import base64
import pathlib
import urllib.request

DEVICON = "https://cdn.jsdelivr.net/gh/devicons/devicon/icons"
SIMPLE = "https://cdn.jsdelivr.net/npm/simple-icons@13/icons"

# (label, icon source). "simple:" sources come from simple-icons and are
# monochrome, so they carry a tint colour; devicon ships no CUDA or NVIDIA logo.
ICONS = [
    ("Python", "python/python-original"),
    ("TypeScript", "typescript/typescript-original"),
    ("JavaScript", "javascript/javascript-original"),
    ("C++", "cplusplus/cplusplus-original"),
    ("Java", "java/java-original"),
    ("Swift", "swift/swift-original"),
    ("PyTorch", "pytorch/pytorch-original"),
    ("CUDA", "simple:nvidia#76B900"),
    ("NumPy", "numpy/numpy-original"),
    ("pandas", "pandas/pandas-original"),
    ("scikit-learn", "scikitlearn/scikitlearn-original"),
    ("Jupyter", "jupyter/jupyter-original"),
    ("React", "react/react-original"),
    ("Next.js", "nextjs/nextjs-original"),
    ("Tailwind", "tailwindcss/tailwindcss-original"),
    ("Three.js", "threejs/threejs-original"),
    ("Node.js", "nodejs/nodejs-original"),
    ("Express", "express/express-original"),
    ("FastAPI", "fastapi/fastapi-original"),
    ("HTML5", "html5/html5-original"),
    ("CSS3", "css3/css3-original"),
    ("PostgreSQL", "postgresql/postgresql-original"),
    ("MySQL", "mysql/mysql-original"),
    ("MongoDB", "mongodb/mongodb-original"),
    ("Supabase", "supabase/supabase-original"),
    ("Docker", "docker/docker-original"),
    ("Google Cloud", "googlecloud/googlecloud-original"),
    ("AWS", "amazonwebservices/amazonwebservices-original-wordmark"),
    ("Vercel", "vercel/vercel-original"),
    ("Git", "git/git-original"),
]

ICON = 40          # logo box, px
CHIP_W = 92        # rounded tile width, px
CHIP_H = 84        # rounded tile height, px
GAP = 14           # space between tiles, px
HEIGHT = 100       # svg height, px
VIEW_W = 880       # visible width, px
SECONDS = 50       # one full loop
LABEL_SIZE = 11.5  # caption size, px

# No webfonts: an <img>-loaded SVG cannot fetch anything external, so captions
# fall back through the viewer's own system stack.
FONT = "system-ui,-apple-system,'Segoe UI',Roboto,Helvetica,Arial,sans-serif"

# Several devicon logos are near-black (Next.js, Vercel, Express, Three.js,
# AWS). A light tile behind every logo keeps the strip readable on GitHub's
# dark theme and stays near-invisible on the light one.


def fetch(source: str) -> str:
    if source.startswith("simple:"):
        name, _, colour = source[len("simple:"):].partition("#")
        url = f"{SIMPLE}/{name}.svg"
    else:
        name, colour, url = source, "", f"{DEVICON}/{source}.svg"
    with urllib.request.urlopen(url, timeout=30) as r:
        raw = r.read()
    if colour:
        raw = raw.replace(b"<path ", f'<path fill="#{colour}" '.encode(), 1)
    return base64.b64encode(raw).decode("ascii")


def main() -> None:
    step = CHIP_W + GAP
    strip_w = step * len(ICONS)
    chip_y = (HEIGHT - CHIP_H) / 2
    icon_y = chip_y + 13
    label_y = chip_y + CHIP_H - 16

    tiles = []
    for i, (label, source) in enumerate(ICONS):
        b64 = fetch(source)
        x = i * step
        mid = x + CHIP_W / 2
        tiles.append(
            f'    <g>\n'
            f'      <rect x="{x}" y="{chip_y:g}" width="{CHIP_W}" height="{CHIP_H}" rx="16" '
            f'fill="#ffffff" fill-opacity="0.94" stroke="#0f172a" stroke-opacity="0.08"/>\n'
            f'      <image x="{mid - ICON / 2:g}" y="{icon_y:g}" width="{ICON}" height="{ICON}" '
            f'href="data:image/svg+xml;base64,{b64}"/>\n'
            f'      <text x="{mid:g}" y="{label_y:g}" text-anchor="middle" '
            f'font-family="{FONT}" font-size="{LABEL_SIZE}" font-weight="500" '
            f'fill="#0f172a" fill-opacity="0.82">{label.replace("&", "&amp;")}</text>\n'
            f'    </g>'
        )
        print(f"  fetched {label}")

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{VIEW_W}" height="{HEIGHT}" viewBox="0 0 {VIEW_W} {HEIGHT}" role="img" aria-label="Tech stack">
  <style>
    @keyframes scroll {{
      from {{ transform: translateX(0); }}
      to   {{ transform: translateX(-{strip_w}px); }}
    }}
    .track {{ animation: scroll {SECONDS}s linear infinite; }}
    @media (prefers-reduced-motion: reduce) {{ .track {{ animation: none; }} }}
  </style>
  <defs>
    <g id="strip">
{chr(10).join(tiles)}
    </g>
    <linearGradient id="fade" x1="0" x2="1">
      <stop offset="0" stop-color="#fff" stop-opacity="0"/>
      <stop offset="0.05" stop-color="#fff" stop-opacity="1"/>
      <stop offset="0.95" stop-color="#fff" stop-opacity="1"/>
      <stop offset="1" stop-color="#fff" stop-opacity="0"/>
    </linearGradient>
    <mask id="edges">
      <rect width="{VIEW_W}" height="{HEIGHT}" fill="url(#fade)"/>
    </mask>
  </defs>
  <g mask="url(#edges)">
    <g class="track">
      <use xlink:href="#strip" x="0"/>
      <use xlink:href="#strip" x="{strip_w}"/>
    </g>
  </g>
</svg>
'''

    out = pathlib.Path(__file__).resolve().parent.parent / "assets" / "tech-stack.svg"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(svg, encoding="utf-8")
    print(f"wrote {out} ({out.stat().st_size / 1024:.0f} KB, {len(ICONS)} icons)")


if __name__ == "__main__":
    main()
