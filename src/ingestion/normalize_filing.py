import re
from pathlib import Path

from bs4 import BeautifulSoup


ITEM_PATTERN = re.compile(
    r"^Item\s+(\d+[A-Z]?)\.\s+(.+)$",
    re.IGNORECASE,
)

PART_PATTERN = re.compile(
    r"^Part\s+(I{1,3}|IV)\b",
    re.IGNORECASE,
)

PAGE_HEADER_PATTERN = re.compile(
    r"^.+\s*\|\s*\d{4}\s+Form\s+(10-K|10-Q)\s*\|\s*\d+$",
    re.IGNORECASE,
)


def normalize_whitespace(text: str) -> str:
    """Normalize whitespace in extracted text."""

    text = text.replace("\xa0", " ")

    return re.sub(
        r"\s+",
        " ",
        text,
    ).strip()


def is_page_header(text: str) -> bool:
    """Identify recurring SEC filing page headers."""

    text = normalize_whitespace(text)

    return bool(
        PAGE_HEADER_PATTERN.match(text)
    )


def is_item_heading(element) -> bool:
    """
    Return True when a body-level element contains
    an actual SEC Item heading.
    """

    if element.name != "div":
        return False

    span = element.find(
        "span",
        recursive=False,
    )

    if span is None:
        return False

    text = normalize_whitespace(
        span.get_text(
            " ",
            strip=True,
        )
    )

    if not ITEM_PATTERN.match(text):
        return False

    style = span.get(
        "style",
        "",
    ).lower()

    return "font-weight:700" in style


def is_part_heading(element) -> bool:
    """Return True when an element is a Part I/II/III/IV heading."""

    text = normalize_whitespace(
        element.get_text(
            " ",
            strip=True,
        )
    )

    return bool(
        PART_PATTERN.match(text)
    )


def is_signature_boundary(element) -> bool:
    """
    Detect the beginning of the signature/Power of Attorney
    boilerplate at the end of the filing.
    """

    text = normalize_whitespace(
        element.get_text(
            " ",
            strip=True,
        )
    )

    return text.upper() == "SIGNATURES"


def extract_item_metadata(element):
    """Extract Item number and title from an Item heading."""

    span = element.find(
        "span",
        recursive=False,
    )

    if span is None:
        return None

    text = normalize_whitespace(
        span.get_text(
            " ",
            strip=True,
        )
    )

    match = ITEM_PATTERN.match(text)

    if not match:
        return None

    return {
        "item_number": match.group(1).upper(),
        "title": match.group(2).strip(),
    }


def clean_table_row(values: list[str]) -> str:
    """
    Remove empty table cells and return a compact row.

    SEC filing tables frequently contain empty cells used only
    for visual layout. Those cells do not carry evidence.
    """

    cleaned_values = [
        value
        for value in values
        if value
    ]

    return " | ".join(cleaned_values)


def table_to_text(table) -> str:
    """
    Convert an HTML table into readable row-based text.

    Example:

        Metric | 2025 | 2024 | 2023
        Revenue | 416,161 | 391,035 | 383,285
    """

    rows = table.find_all(
        "tr"
    )

    extracted_rows = []

    for row in rows:

        cells = row.find_all(
            ["td", "th"],
            recursive=False,
        )

        if not cells:
            continue

        values = []

        for cell in cells:

            text = normalize_whitespace(
                cell.get_text(
                    " ",
                    strip=True,
                )
            )

            values.append(text)

        row_text = clean_table_row(
            values
        )

        if row_text:
            extracted_rows.append(
                row_text
            )

    return "\n".join(
        extracted_rows
    )


def extract_block_content(
    block,
) -> tuple[str, list[str]]:
    """
    Extract ordinary text and tables from one body-level block.

    Tables are returned separately so that their contents are not
    duplicated inside the ordinary text representation.
    """

    table_contents = []

    tables = block.find_all(
        "table"
    )

    for table in tables:

        table_text = table_to_text(
            table
        )

        if table_text:
            table_contents.append(
                table_text
            )

    # Create a copy so table contents can be removed from
    # ordinary text extraction.
    block_copy = BeautifulSoup(
        str(block),
        "html.parser",
    )

    for table in block_copy.find_all(
        "table"
    ):
        table.decompose()

    text = normalize_whitespace(
        block_copy.get_text(
            " ",
            strip=True,
        )
    )

    if is_page_header(text):
        text = ""

    return text, table_contents


def save_current_section(
    sections: list,
    current_section: dict | None,
    current_content: list[str],
    current_tables: list[str],
):
    """Finalize and append the current section."""

    if current_section is None:
        return

    text = "\n".join(
        item
        for item in current_content
        if item
    ).strip()

    current_section["text"] = text
    current_section["tables"] = current_tables

    sections.append(
        current_section
    )


def normalize_filing(
    filing_path: Path,
    filing_metadata: dict,
):
    """
    Convert a raw SEC filing into structured sections.

    Processing flow:

        Raw SEC HTML
            ↓
        Body-level traversal
            ↓
        Part detection
            ↓
        Item detection
            ↓
        Text + table extraction
            ↓
        Page-header removal
            ↓
        Signature boundary
            ↓
        Structured sections
    """

    html = filing_path.read_text(
        encoding="utf-8"
    )

    soup = BeautifulSoup(
        html,
        "html.parser",
    )

    if soup.body is None:
        raise ValueError(
            "Filing HTML does not contain a <body> element."
        )

    sections = []

    current_part = None
    current_section = None

    current_content = []
    current_tables = []

    document_ended = False

    # The actual SEC filing structure places the meaningful
    # document content in direct children of <body>.
    for block in soup.body.find_all(
        recursive=False
    ):

        if not getattr(
            block,
            "name",
            None,
        ):
            continue

        # --------------------------------------------------
        # 1. Stop at signature boilerplate
        # --------------------------------------------------

        if is_signature_boundary(block):

            save_current_section(
                sections,
                current_section,
                current_content,
                current_tables,
            )

            document_ended = True
            break

        # --------------------------------------------------
        # 2. Detect Part headings
        # --------------------------------------------------

        if is_part_heading(block):

            current_part = normalize_whitespace(
                block.get_text(
                    " ",
                    strip=True,
                )
            )

            continue

        # --------------------------------------------------
        # 3. Detect Item headings
        # --------------------------------------------------

        if is_item_heading(block):

            save_current_section(
                sections,
                current_section,
                current_content,
                current_tables,
            )

            metadata = extract_item_metadata(
                block
            )

            if metadata is None:
                continue

            current_section = {
                "part": current_part,
                "item_number": metadata[
                    "item_number"
                ],
                "title": metadata[
                    "title"
                ],
                "text": "",
                "tables": [],
            }

            current_content = []
            current_tables = []

            continue

        # --------------------------------------------------
        # 4. Ignore everything before first Item
        # --------------------------------------------------

        if current_section is None:
            continue

        # --------------------------------------------------
        # 5. Extract text and tables
        # --------------------------------------------------

        text, tables = extract_block_content(
            block
        )

        if text:
            current_content.append(
                text
            )

        if tables:
            current_tables.extend(
                tables
            )

    # ------------------------------------------------------
    # 6. Save final section if EOF was reached normally
    # ------------------------------------------------------

    if not document_ended:

        save_current_section(
            sections,
            current_section,
            current_content,
            current_tables,
        )

    return {
        "metadata": filing_metadata,
        "sections": sections,
    }