#!/usr/bin/env python3
"""
The Pivot Path — a custom generative SVG for a 90-day challenge.
Reads days.json (array of day completion records) and renders a winding
path where each day is a node, colored by completion %, with the current
day highlighted distinctly.

days.json format:
[
  {"day": 1, "score": 6},   // score = number of 7 pillars completed that day (0-7)
  {"day": 2, "score": 4},
  ...
]
Days not yet reached are simply absent from the list.
"""

import json
import math
import os

TOTAL_DAYS = 90
WIDTH = 1200
HEIGHT = 260
NODE_RADIUS = 6
PATH_AMPLITUDE = 60   # vertical wave height
PATH_PADDING_X = 30

# Brand palette (matches the Monk Mode tracker / LinkedIn theme)
COLOR_BG = "#1B1814"
COLOR_LINE = "#3C3327"
COLOR_EMPTY = "#241F19"
COLOR_LOW = "#5C4A2E"      # low completion (1-3)
COLOR_MID = "#8A5B2C"      # mid completion (4-5)
COLOR_HIGH = "#C1813F"     # high completion (6-7)
COLOR_TODAY_RING = "#E9E0CD"
COLOR_TEXT = "#A89C84"


def load_days(path="days.json"):
    if not os.path.exists(path):
        return {}
    with open(path, "r") as f:
        data = json.load(f)
    return {entry["day"]: entry["score"] for entry in data}


def node_color(score):
    if score is None:
        return COLOR_EMPTY
    if score >= 6:
        return COLOR_HIGH
    if score >= 4:
        return COLOR_MID
    if score >= 1:
        return COLOR_LOW
    return COLOR_EMPTY


def node_position(i, total=TOTAL_DAYS):
    """Place node i along a horizontal sine wave."""
    x = PATH_PADDING_X + (WIDTH - 2 * PATH_PADDING_X) * (i / (total - 1))
    y = HEIGHT / 2 + PATH_AMPLITUDE * math.sin(i * 0.35)
    return x, y


def build_svg(days_scores):
    today = max(days_scores.keys(), default=1)
    points = [node_position(i) for i in range(TOTAL_DAYS)]

    # Build the connecting path (smooth line through all nodes)
    path_d = f"M {points[0][0]:.1f} {points[0][1]:.1f} "
    for x, y in points[1:]:
        path_d += f"L {x:.1f} {y:.1f} "

    svg_parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}" width="100%">',
        f'<rect width="{WIDTH}" height="{HEIGHT}" fill="{COLOR_BG}" rx="14"/>',
        f'<path d="{path_d}" stroke="{COLOR_LINE}" stroke-width="2" fill="none" opacity="0.6"/>',
        f'<text x="{PATH_PADDING_X}" y="30" fill="{COLOR_TEXT}" font-family="Fira Code, monospace" font-size="14">THE PIVOT PATH — DAY {today} / {TOTAL_DAYS}</text>',
    ]

    for i in range(TOTAL_DAYS):
        day_num = i + 1
        x, y = points[i]
        score = days_scores.get(day_num)
        color = node_color(score)

        if day_num == today:
            # glowing ring around today's node
            svg_parts.append(
                f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{NODE_RADIUS + 6}" '
                f'fill="none" stroke="{COLOR_TODAY_RING}" stroke-width="2">'
                f'<animate attributeName="r" values="{NODE_RADIUS+4};{NODE_RADIUS+9};{NODE_RADIUS+4}" '
                f'dur="2s" repeatCount="indefinite"/>'
                f'<animate attributeName="opacity" values="1;0.3;1" dur="2s" repeatCount="indefinite"/>'
                f'</circle>'
            )
            r = NODE_RADIUS + 2
        else:
            r = NODE_RADIUS if day_num <= today else NODE_RADIUS - 2
            opacity = 1.0 if day_num <= today else 0.25

        svg_parts.append(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{color}" '
            f'opacity="{1.0 if day_num == today else (1.0 if day_num <= today else 0.25)}"/>'
        )

    svg_parts.append(
        f'<text x="{WIDTH - 30}" y="{HEIGHT - 16}" fill="{COLOR_TEXT}" '
        f'font-family="Fira Code, monospace" font-size="12" text-anchor="end">'
        f'7 pillars/day · {len([d for d in days_scores if days_scores[d] >= 6])} strong days so far</text>'
    )
    svg_parts.append('</svg>')
    return "\n".join(svg_parts)


def main():
    days_scores = load_days()
    svg = build_svg(days_scores)
    os.makedirs("dist", exist_ok=True)
    with open("dist/pivot-path.svg", "w") as f:
        f.write(svg)
    print(f"Generated dist/pivot-path.svg with {len(days_scores)} recorded days")


if __name__ == "__main__":
    main()
