import json
import os
from pathlib import Path

import requests
from bs4 import BeautifulSoup

username = os.getenv("GITHUB_USERNAME", "cigddemakcan")

url = f"https://github.com/users/{username}/contributions"

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(url, headers=headers, timeout=30)
response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")

contributions = []

for cell in soup.select("td.ContributionCalendar-day"):
    date = cell.get("data-date")

    if not date:
        continue

    level = int(cell.get("data-level", 0))

    contributions.append({
        "date": date,
        "level": level
    })

Path("data").mkdir(exist_ok=True)

with open("data/contributions.json", "w", encoding="utf-8") as file:
    json.dump(
        {
            "username": username,
            "contributions": contributions
        },
        file,
        indent=2
    )

print(f"Saved {len(contributions)} contribution days.")
