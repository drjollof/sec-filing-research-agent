from pathlib import Path

from bs4 import BeautifulSoup


FILING_PATH = Path(
    "data/raw/AAPL/0000320193-25-000079.html"
)


html = FILING_PATH.read_text(
    encoding="utf-8"
)

soup = BeautifulSoup(
    html,
    "html.parser",
)


tables = soup.body.find_all("table")

print("=" * 80)
print("TABLE CONTENT INSPECTION")
print("=" * 80)

found = 0

for i, table in enumerate(tables, start=1):

    text = table.get_text(
        " ",
        strip=True,
    )

    if len(text) < 50:
        continue

    found += 1

    print("\n" + "-" * 80)
    print(f"TABLE #{i}")
    print(f"Text length: {len(text):,}")
    print(f"Preview:\n{text[:1000]}")

    if found >= 5:
        break


print("\n" + "=" * 80)
print(f"DATA-BEARING TABLES SHOWN: {found}")
print("=" * 80)