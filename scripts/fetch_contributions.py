import json
import os
from pathlib import Path

import requests
from bs4 import BeautifulSoup


USERNAME = os.getenv("GITHUB_USERNAME", "cigddemakcan")
URL = f"https://github.com/users/{USERNAME}/contributions"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def fetch_contributions():
    response = requests.get(URL, headers=HEADERS, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    contributions = []

    for cell in soup.select("td.ContributionCalendar-day"):
        date = cell.get("data-date")

        if not date:
            continue

        level = int(cell.get("data-level", "0"))

        tooltip_id = cell.get("id")
        count = 0

        if tooltip_id:
            tooltip = soup.select_one(
                f'tool-tip[for="{tooltip_id}"]'
            )

            if tooltip:
                text = tooltip.get_text(" ", strip=True)

                first_word = text.split()[0]

                if first_word.isdigit():
                    count = int(first_word)

        contributions.append(
            {
                "date": date,
                "level": level,
                "count": count,
            }
        )

    if not contributions:
        raise RuntimeError(
            "No contribution cells were found."
        )

    return contributions


def save_contributions(contributions):
    Path("data").mkdir(parents=True, exist_ok=True)

    output = {
        "username": USERNAME,
        "total": sum(item["count"] for item in contributions),
        "contributions": contributions,
    }

    with open(
        "data/contributions.json",
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            output,
            file,
            indent=2,
            ensure_ascii=False,
        )

    print(
        f"Saved {len(contributions)} contribution days "
        f"for {USERNAME}."
    )


if __name__ == "__main__":
    data = fetch_contributions()
    save_contributions(data)
