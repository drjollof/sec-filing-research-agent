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

table = soup.body.find("table")


print("=" * 80)
print("FIRST TABLE STRUCTURE")
print("=" * 80)

print("\nTABLE HTML:")
print(table.prettify()[:10000])

print("\n" + "=" * 80)
print("TABLE ROW/CELL COUNTS")
print("=" * 80)

rows = table.find_all("tr")

print(f"Rows found: {len(rows)}")

for i, row in enumerate(rows[:10], start=1):

    cells = row.find_all(
        ["td", "th"]
    )

    print(
        f"Row {i}: "
        f"{len(cells)} cells"
    )

    for j, cell in enumerate(cells[:10], start=1):

        print(
            f"  Cell {j}: "
            f"{repr(cell.get_text(' ', strip=True))}"
        )