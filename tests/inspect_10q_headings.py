import re
from pathlib import Path

from bs4 import BeautifulSoup


FILING_PATH = Path(
    "data/raw/AAPL/0000320193-26-000020.html"
)


ITEM_PATTERN = re.compile(
    r"^Item\s+\d+[A-Z]?\.\s+.+",
    re.IGNORECASE,
)


html = FILING_PATH.read_text(
    encoding="utf-8"
)

soup = BeautifulSoup(
    html,
    "html.parser",
)


print("=" * 80)
print("10-Q ITEM HEADING INSPECTION")
print("=" * 80)

candidates = []


for span in soup.find_all("span"):

    text = span.get_text(
        " ",
        strip=True,
    )

    if not text:
        continue

    if not ITEM_PATTERN.match(text):
        continue

    style = span.get("style", "").lower()

    candidates.append(
        {
            "text": text,
            "style": style,
            "parent": span.parent.name
            if span.parent
            else None,
        }
    )


print(
    f"\nPotential Item headings found: "
    f"{len(candidates)}"
)


for i, candidate in enumerate(
    candidates,
    start=1,
):

    print(
        f"\n{i}. {candidate['text']}"
    )

    print(
        f"   Parent: <{candidate['parent']}>"
    )

    print(
        f"   Bold style: "
        f"{'font-weight:700' in candidate['style']}"
    )