from pathlib import Path

from bs4 import BeautifulSoup


FILING_PATH = Path(
    "data/raw/AAPL/0000320193-25-000079.html"
)


SECTION_MARKERS = [
    "ITEM 1",
    "ITEM 1A",
    "ITEM 1B",
    "ITEM 2",
    "ITEM 3",
    "ITEM 4",
    "ITEM 5",
    "ITEM 6",
    "ITEM 7",
    "ITEM 7A",
    "ITEM 8",
    "ITEM 9",
    "ITEM 9A",
    "ITEM 9B",
    "ITEM 9C",
    "ITEM 10",
    "ITEM 11",
    "ITEM 12",
    "ITEM 13",
    "ITEM 14",
    "ITEM 15",
]


html = FILING_PATH.read_text(
    encoding="utf-8"
)

soup = BeautifulSoup(
    html,
    "html.parser",
)


print("=" * 80)
print("SEC FILING SECTION INSPECTION")
print("=" * 80)

print(f"\nFile: {FILING_PATH}")
print(f"HTML size: {len(html):,} characters")


for marker in SECTION_MARKERS:

    matches = soup.find_all(
        string=lambda text: (
            text
            and marker.lower() in text.lower()
        )
    )

    if not matches:
        print(
            f"\n{marker}: NOT FOUND"
        )
        continue

    print(
        f"\n{'-' * 80}"
    )
    print(
        f"{marker}: {len(matches)} occurrence(s)"
    )
    print(
        f"{'-' * 80}"
    )

    for number, text_node in enumerate(
        matches[:3],
        start=1,
    ):

        text = text_node.strip()

        print(
            f"\nOccurrence {number}:"
        )

        print(
            f"Text: {text[:300]!r}"
        )

        parent = text_node.parent

        print(
            f"Parent tag: <{parent.name}>"
        )

        print(
            f"Parent attributes: "
            f"{dict(parent.attrs)}"
        )

        print(
            "\nParent HTML:"
        )

        print(
            parent.prettify()[:1500]
        )