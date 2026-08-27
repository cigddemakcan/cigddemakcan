import json
from datetime import datetime
from pathlib import Path

DATA_FILE = Path("data/contributions.json")
OUTPUT_FILE = Path("contrib-heatmap.svg")

WIDTH = 1000
HEIGHT = 310

CELL = 12
GAP = 4

GRID_X = 55
GRID_Y = 135

BG = "#0d1117"
CARD = "#0d1117"
BORDER = "#30363d"

TEXT = "#f0f6fc"
MUTED = "#8b949e"

LEVEL_COLORS = {
    0: "#161b22",
    1: "#1e3a5f",
    2: "#245b8a",
    3: "#2f81f7",
    4: "#79c0ff",
}


def load_data():
    with DATA_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def sunday_index(date):
    # Python: Monday=0 ... Sunday=6
    # GitHub calendar: Sunday=0 ... Saturday=6
    return (date.weekday() + 1) % 7


def calculate_streak(contributions):
    longest = 0
    current = 0

    for item in contributions:
        if item["count"] > 0:
            current += 1
            longest = max(longest, current)
        else:
            current = 0

    return longest


def render():
    data = load_data()
    contributions = data["contributions"]

    if not contributions:
        raise RuntimeError("Contribution data is empty.")

    contributions.sort(key=lambda item: item["date"])

    total = data.get(
        "total",
        sum(item["count"] for item in contributions)
    )

    active_days = sum(
        1 for item in contributions
        if item["count"] > 0
    )

    longest_streak = calculate_streak(contributions)

    first_date = datetime.strptime(
        contributions[0]["date"],
        "%Y-%m-%d"
    )

    first_day_offset = sunday_index(first_date)

    svg = []

    svg.append(
        f"""
<svg
    xmlns="http://www.w3.org/2000/svg"
    width="{WIDTH}"
    height="{HEIGHT}"
    viewBox="0 0 {WIDTH} {HEIGHT}"
>

<style>
    .title {{
        font-family: -apple-system, BlinkMacSystemFont,
                     "Segoe UI", sans-serif;
        font-size: 24px;
        font-weight: 700;
        fill: {TEXT};
    }}

    .subtitle {{
        font-family: "JetBrains Mono", monospace;
        font-size: 13px;
        fill: {MUTED};
    }}

    .stat-number {{
        font-family: "JetBrains Mono", monospace;
        font-size: 20px;
        font-weight: 700;
        fill: {TEXT};
    }}

    .stat-label {{
        font-family: -apple-system, BlinkMacSystemFont,
                     "Segoe UI", sans-serif;
        font-size: 11px;
        fill: {MUTED};
    }}

    .day-label {{
        font-family: "JetBrains Mono", monospace;
        font-size: 10px;
        fill: {MUTED};
    }}
</style>

<rect
    x="1"
    y="1"
    width="{WIDTH - 2}"
    height="{HEIGHT - 2}"
    rx="18"
    fill="{CARD}"
    stroke="{BORDER}"
/>

<text x="42" y="45" class="title">
    Contribution Activity
</text>

<text x="42" y="70" class="subtitle">
    github.com/{data["username"]}
</text>

<line
    x1="42"
    y1="92"
    x2="{WIDTH - 42}"
    y2="92"
    stroke="{BORDER}"
/>

<text x="55" y="118" class="stat-number">
    {total}
</text>

<text x="55" y="134" class="stat-label">
    CONTRIBUTIONS
</text>

<text x="225" y="118" class="stat-number">
    {active_days}
</text>

<text x="225" y="134" class="stat-label">
    ACTIVE DAYS
</text>

<text x="365" y="118" class="stat-number">
    {longest_streak}
</text>

<text x="365" y="134" class="stat-label">
    LONGEST STREAK
</text>
"""
    )

    labels = [
        ("Mon", 1),
        ("Wed", 3),
        ("Fri", 5),
    ]

    for label, day in labels:
        y = GRID_Y + day * (CELL + GAP) + 10

        svg.append(
            f"""
<text
    x="18"
    y="{y}"
    class="day-label"
>
    {label}
</text>
"""
        )

    for index, item in enumerate(contributions):
        date = datetime.strptime(
            item["date"],
            "%Y-%m-%d"
        )

        position = index + first_day_offset

        week = position // 7
        weekday = sunday_index(date)

        x = GRID_X + week * (CELL + GAP)
        y = GRID_Y + weekday * (CELL + GAP)

        color = LEVEL_COLORS.get(
            item["level"],
            LEVEL_COLORS[0]
        )

        delay = (
            week * 0.025
            + weekday * 0.008
        )

        svg.append(
            f"""
<rect
    x="{x}"
    y="{y}"
    width="{CELL}"
    height="{CELL}"
    rx="3"
    fill="{color}"
    opacity="0"
>
    <animate
        attributeName="opacity"
        from="0"
        to="1"
        dur="0.35s"
        begin="{delay:.2f}s"
        fill="freeze"
    />
</rect>
"""
        )

    svg.append(
        f"""
<text
    x="55"
    y="{HEIGHT - 28}"
    class="subtitle"
>
    Java • Spring Boot • Backend Development
</text>

<circle
    cx="{WIDTH - 58}"
    cy="{HEIGHT - 33}"
    r="5"
    fill="#58a6ff"
>
    <animate
        attributeName="opacity"
        values="1;0.25;1"
        dur="2s"
        repeatCount="indefinite"
    />
</circle>

<text
    x="{WIDTH - 145}"
    y="{HEIGHT - 28}"
    class="subtitle"
>
    active
</text>

</svg>
"""
    )

    OUTPUT_FILE.write_text(
        "".join(svg),
        encoding="utf-8"
    )

    print(
        f"Generated {OUTPUT_FILE}"
    )


if __name__ == "__main__":
    render()
