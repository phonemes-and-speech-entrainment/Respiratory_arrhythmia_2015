#!/usr/bin/env python3
"""Render HH1neuron output as a dependency-free SVG plot."""

import argparse
import html
import math
from pathlib import Path


HERE = Path(__file__).resolve().parent

WIDTH = 1200
HEIGHT = 760
LEFT = 115
RIGHT = 1140
TIME_MIN = -1000.0
TIME_MAX = 1000.0
CURRENT_MIN = 0.0
CURRENT_TOP = 100.0
CURRENT_BOTTOM = 240.0
VOLTAGE_TOP = 330.0
VOLTAGE_BOTTOM = 650.0


def x_position(time):
    return LEFT + (time - TIME_MIN) / (TIME_MAX - TIME_MIN) * (RIGHT - LEFT)


def y_position(value, minimum, maximum, top, bottom):
    return bottom - (value - minimum) / (maximum - minimum) * (bottom - top)


def path_for(rows, value_index, minimum, maximum, top, bottom):
    points = []
    for row in rows:
        x = x_position(row[0])
        y = y_position(row[value_index], minimum, maximum, top, bottom)
        points.append(f"{x:.2f},{y:.2f}")
    return "M" + " L".join(points)


def render(data_file, svg_file, title):
    rows = []
    with data_file.open(encoding="ascii") as input_file:
        for line_number, line in enumerate(input_file, start=1):
            fields = line.split()
            if len(fields) != 3:
                raise ValueError(f"{data_file}:{line_number}: expected 3 columns")
            row = tuple(map(float, fields))
            if not all(math.isfinite(value) for value in row):
                raise ValueError(f"{data_file}:{line_number}: non-finite value")
            rows.append(row)
    if not rows:
        raise ValueError(f"{data_file}: no simulation data")

    current_max = max(5.0, math.ceil(max(row[1] for row in rows) / 5.0) * 5.0)
    voltage_min = math.floor(min(row[2] for row in rows) / 25.0) * 25.0
    voltage_max = math.ceil(max(row[2] for row in rows) / 25.0) * 25.0
    if voltage_min == voltage_max:
        voltage_max += 25.0

    text = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" '
        f'viewBox="0 0 {WIDTH} {HEIGHT}">',
        "<style>",
        "text{font-family:Arial,Helvetica,sans-serif;fill:#202124}",
        ".tick{font-size:14px}.label{font-size:17px}.title{font-size:24px;font-weight:bold}",
        ".grid{stroke:#d9dee5;stroke-width:1}.axis{stroke:#333;stroke-width:1.5}",
        "</style>",
        '<rect width="100%" height="100%" fill="white"/>',
        f'<text class="title" x="600" y="42" text-anchor="middle">{html.escape(title)}</text>',
    ]

    time_ticks = (-1000, -500, 0, 500, 1000)
    for tick in time_ticks:
        x = x_position(tick)
        text.extend(
            [
                f'<line class="grid" x1="{x:.2f}" y1="{CURRENT_TOP}" x2="{x:.2f}" y2="{VOLTAGE_BOTTOM}"/>',
                f'<text class="tick" x="{x:.2f}" y="{VOLTAGE_BOTTOM + 24}" text-anchor="middle">{tick}</text>',
            ]
        )

    for tick in (0, current_max / 2, current_max):
        y = y_position(tick, CURRENT_MIN, current_max, CURRENT_TOP, CURRENT_BOTTOM)
        text.extend(
            [
                f'<line class="grid" x1="{LEFT}" y1="{y:.2f}" x2="{RIGHT}" y2="{y:.2f}"/>',
                f'<text class="tick" x="{LEFT - 12}" y="{y + 5:.2f}" text-anchor="end">{tick:g}</text>',
            ]
        )
    for tick in range(int(voltage_min), int(voltage_max) + 1, 25):
        y = y_position(tick, voltage_min, voltage_max, VOLTAGE_TOP, VOLTAGE_BOTTOM)
        text.extend(
            [
                f'<line class="grid" x1="{LEFT}" y1="{y:.2f}" x2="{RIGHT}" y2="{y:.2f}"/>',
                f'<text class="tick" x="{LEFT - 12}" y="{y + 5:.2f}" text-anchor="end">{tick}</text>',
            ]
        )

    text.extend(
        [
            f'<line class="axis" x1="{LEFT}" y1="{CURRENT_TOP}" x2="{LEFT}" y2="{CURRENT_BOTTOM}"/>',
            f'<line class="axis" x1="{LEFT}" y1="{CURRENT_BOTTOM}" x2="{RIGHT}" y2="{CURRENT_BOTTOM}"/>',
            f'<line class="axis" x1="{LEFT}" y1="{VOLTAGE_TOP}" x2="{LEFT}" y2="{VOLTAGE_BOTTOM}"/>',
            f'<line class="axis" x1="{LEFT}" y1="{VOLTAGE_BOTTOM}" x2="{RIGHT}" y2="{VOLTAGE_BOTTOM}"/>',
            '<text class="label" x="628" y="88" text-anchor="middle">Applied current (units unspecified)</text>',
            '<text class="label" x="628" y="305" text-anchor="middle">Membrane voltage (units unspecified)</text>',
            f'<text class="label" x="628" y="714" text-anchor="middle">Time (units unspecified)</text>',
            f'<text class="label" transform="translate(30 170) rotate(-90)" text-anchor="middle">Applied current (units unspecified)</text>',
            f'<text class="label" transform="translate(30 490) rotate(-90)" text-anchor="middle">Membrane voltage (units unspecified)</text>',
            f'<path d="{path_for(rows, 1, CURRENT_MIN, current_max, CURRENT_TOP, CURRENT_BOTTOM)}" '
            'fill="none" stroke="#d97706" stroke-width="2"/>',
            f'<path d="{path_for(rows, 2, voltage_min, voltage_max, VOLTAGE_TOP, VOLTAGE_BOTTOM)}" '
            'fill="none" stroke="#1769aa" stroke-width="1.5"/>',
            '<line x1="860" y1="68" x2="890" y2="68" stroke="#d97706" stroke-width="3"/>',
            '<text class="tick" x="898" y="73">Applied current</text>',
            '<line x1="1020" y1="68" x2="1050" y2="68" stroke="#1769aa" stroke-width="3"/>',
            '<text class="tick" x="1058" y="73">Voltage</text>',
            "</svg>",
        ]
    )
    svg_file.write_text("\n".join(text) + "\n", encoding="utf-8")
    print(f"Wrote {svg_file} from {len(rows)} data rows")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=HERE / "HH1neuron.dat")
    parser.add_argument("--output", type=Path, default=HERE / "HH1neuron.svg")
    parser.add_argument("--title", default="HH1neuron simulation output")
    arguments = parser.parse_args()
    render(arguments.data, arguments.output, arguments.title)
