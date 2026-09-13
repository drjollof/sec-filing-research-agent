from pathlib import Path

from bs4 import BeautifulSoup


filing_path = Path(
    "data/raw/AAPL/0000320193-25-000079.html"
)


html = filing_path.read_text(
    encoding="utf-8"
)


print(f"HTML size: {len(html):,} characters")


soup = BeautifulSoup(
    html,
    "html.parser",
)


print(f"Title: {soup.title.get_text(strip=True)}")


headings = soup.find_all(
    ["h1", "h2", "h3", "h4", "h5", "h6"]
)


print(f"HTML heading elements: {len(headings)}")


print("\nFirst 30 headings:\n")

for heading in headings[:30]:
    text = heading.get_text(
        " ",
        strip=True,
    )

    if text:
        print(
            f"{heading.name}: {text[:200]}"
        )