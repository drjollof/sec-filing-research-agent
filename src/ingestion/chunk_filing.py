from dataclasses import asdict, dataclass
from typing import Optional


@dataclass
class DocumentChunk:
    """A retrieval-ready chunk from an SEC filing."""

    chunk_id: str
    company: str
    ticker: str
    cik: str
    form: str
    filing_date: str
    report_date: str
    accession_number: str

    part: Optional[str]
    item_number: str
    item_title: str

    content_type: str
    chunk_index: int

    text: str


def split_text(
    text: str,
    chunk_size: int = 1000,
    overlap: int = 150,
) -> list[str]:
    """
    Split text into overlapping chunks while preserving
    word boundaries.

    chunk_size is the approximate target size in characters.
    overlap is the approximate number of characters shared
    between consecutive chunks.
    """

    if not text.strip():
        return []

    if chunk_size <= 0:
        raise ValueError(
            "chunk_size must be greater than zero."
        )

    if overlap < 0:
        raise ValueError(
            "overlap cannot be negative."
        )

    if overlap >= chunk_size:
        raise ValueError(
            "overlap must be smaller than chunk_size."
        )

    text = text.strip()

    chunks = []

    start = 0
    text_length = len(text)

    while start < text_length:

        target_end = min(
            start + chunk_size,
            text_length,
        )

        # If we have not reached the end, move the boundary
        # backward to the nearest whitespace.
        if target_end < text_length:

            end = text.rfind(
                " ",
                start,
                target_end,
            )

            # Extremely long individual tokens should not
            # cause the boundary to move backwards indefinitely.
            if end <= start:
                end = target_end

        else:
            end = target_end

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= text_length:
            break

        # Start the next chunk before the previous chunk ended
        # to preserve contextual overlap.
        next_start = max(
            end - overlap,
            start + 1,
        )

        # Move the overlap boundary backward to whitespace so
        # the next chunk also starts cleanly.
        if next_start > start:

            boundary = text.find(
                " ",
                next_start,
                end,
            )

            if boundary != -1:
                next_start = boundary + 1

        start = next_start

    return chunks


def build_chunk_id(
    filing_metadata: dict,
    section: dict,
    chunk_index: int,
) -> str:
    """Create a deterministic identifier for a chunk."""

    ticker = filing_metadata["ticker"]
    accession = filing_metadata["accession_number"]
    item_number = section["item_number"]

    return (
        f"{ticker}_"
        f"{accession}_"
        f"item{item_number}_"
        f"chunk{chunk_index:03d}"
    )


def create_chunk(
    filing_metadata: dict,
    section: dict,
    text: str,
    content_type: str,
    chunk_index: int,
) -> DocumentChunk:
    """Create a DocumentChunk with filing provenance."""

    return DocumentChunk(
        chunk_id=build_chunk_id(
            filing_metadata,
            section,
            chunk_index,
        ),
        company=filing_metadata["company"],
        ticker=filing_metadata["ticker"],
        cik=filing_metadata["cik"],
        form=filing_metadata["form"],
        filing_date=filing_metadata["filing_date"],
        report_date=filing_metadata["report_date"],
        accession_number=filing_metadata[
            "accession_number"
        ],
        part=section["part"],
        item_number=section["item_number"],
        item_title=section["title"],
        content_type=content_type,
        chunk_index=chunk_index,
        text=text,
    )


def chunk_section(
    filing_metadata: dict,
    section: dict,
    chunk_size: int = 1000,
    overlap: int = 150,
) -> list[DocumentChunk]:
    """
    Convert one normalized section into retrieval-ready chunks.

    Narrative text is split with overlap.

    Tables are preserved as individual chunks.
    """

    chunks = []

    chunk_index = 0

    # --------------------------------------------------
    # Narrative content
    # --------------------------------------------------

    narrative_chunks = split_text(
        section["text"],
        chunk_size=chunk_size,
        overlap=overlap,
    )

    for text in narrative_chunks:

        chunks.append(
            create_chunk(
                filing_metadata,
                section,
                text,
                content_type="narrative",
                chunk_index=chunk_index,
            )
        )

        chunk_index += 1

    # --------------------------------------------------
    # Table content
    # --------------------------------------------------

    for table in section["tables"]:

        table = table.strip()

        if not table:
            continue

        chunks.append(
            create_chunk(
                filing_metadata,
                section,
                table,
                content_type="table",
                chunk_index=chunk_index,
            )
        )

        chunk_index += 1

    return chunks


def chunk_filing(
    normalized_filing: dict,
    chunk_size: int = 1000,
    overlap: int = 150,
) -> list[DocumentChunk]:
    """
    Convert an entire normalized filing into chunks.
    """

    filing_metadata = normalized_filing["metadata"]

    all_chunks = []

    for section in normalized_filing["sections"]:

        section_chunks = chunk_section(
            filing_metadata,
            section,
            chunk_size=chunk_size,
            overlap=overlap,
        )

        all_chunks.extend(
            section_chunks
        )

    return all_chunks


def chunks_to_dicts(
    chunks: list[DocumentChunk],
) -> list[dict]:
    """Convert DocumentChunk objects to dictionaries."""

    return [
        asdict(chunk)
        for chunk in chunks
    ]