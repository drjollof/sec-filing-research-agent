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


body = soup.body

tables = body.find_all("table")

print("=" * 80)
print(f"TOTAL TABLES: {len(tables)}")
print("=" * 80)


for i, table in enumerate(tables[:5], start=1):

    print("\n" + "-" * 80)
    print(f"TABLE {i}")

    print("\nTable attributes:")
    print(table.attrs)

    print("\nDirect parent:")
    print(table.parent.name)

    print("Parent attributes:")
    print(table.parent.attrs)

    print("\nGrandparent:")
    print(table.parent.parent.name)

    print("Grandparent attributes:")
    print(table.parent.parent.attrs)

    print("\nFirst 500 characters of table text:")
    print(
        table.get_text(
            " ",
            strip=True,
        )[:500]
    )