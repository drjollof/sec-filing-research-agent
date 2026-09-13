import re
from pathlib import Path

from bs4 import BeautifulSoup


FILING_PATH = Path(
    "data/raw/AAPL/0000320193-25-000079.html"
)


TARGETS = [
    re.compile(
        r"^Item\s+1\.\s+Business$",
        re.IGNORECASE,
    ),
    re.compile(
        r"^Item\s+8\.\s+Financial Statements and Supplementary Data$",
        re.IGNORECASE,
    ),
]


html = FILING_PATH.read_text(
    encoding="utf-8"
)

soup = BeautifulSoup(
    html,
    "html.parser",
)


for target in TARGETS:

    print("\n" + "=" * 80)
    print(f"TARGET: {target.pattern}")
    print("=" * 80)

    heading = None

    for span in soup.find_all("span"):

        text = span.get_text(
            " ",
            strip=True,
        )

        # Normalize all whitespace before matching.
        text = re.sub(
            r"\s+",
            " ",
            text,
        ).strip()

        if target.match(text):

            heading = span
            break

    if heading is None:

        print("Heading not found.")
        continue

    print("\nNormalized heading text:")
    print(
        re.sub(
            r"\s+",
            " ",
            heading.get_text(
                " ",
                strip=True,
            ),
        ).strip()
    )

    print("\nHeading element:")
    print(heading)

    print("\nParent:")
    print(heading.parent)

    print("\nParent tag:")
    print(heading.parent.name)

    print("\nParent attributes:")
    print(heading.parent.attrs)

    if heading.parent.parent:

        print("\nGrandparent tag:")
        print(heading.parent.parent.name)

        print("\nGrandparent attributes:")
        print(heading.parent.parent.attrs)

    print("\nPrevious sibling:")
    print(heading.parent.previous_sibling)

    print("\nNext sibling:")
    print(heading.parent.next_sibling)

    print("\nNext 5 element siblings:")

    sibling = heading.parent.next_sibling
    count = 0

    while sibling is not None and count < 5:

        if getattr(
            sibling,
            "name",
            None,
        ):

            print(
                f"\n<{sibling.name}>"
            )

            print(
                sibling.get_text(
                    " ",
                    strip=True,
                )[:500]
            )

            print(
                "Attributes:",
                sibling.attrs,
            )

            count += 1

        sibling = sibling.next_sibling