from dataclasses import dataclass, field
from typing import Any
from src.tools.company_facts import NumericFact
from src.retrieval.retriever import RetrievedChunk


@dataclass
class Evidence:
    source_type: str
    content: str
    provenance: dict[str, Any] = field(default_factory=dict)





class EvidenceNormalizer:

    def from_numeric_fact(
        self,
        fact: NumericFact,
    ) -> Evidence:

        content = (
            f"{fact.label}: "
            f"{fact.value:,} {fact.unit}"
        )

        provenance = {
            "company": fact.company,
            "ticker": fact.ticker,
            "metric": fact.label,
            "concept": fact.fact_name,
            "value": fact.value,
            "unit": fact.unit,
            "fiscal_year": fact.fiscal_year,
            "fiscal_period": fact.fiscal_period,
            "period_start": fact.period_start,
            "period_end": fact.period_end,
            "form": fact.form,
            "filing_date": fact.filing_date,
            "accession_number": fact.accession_number,
        }

        return Evidence(
            source_type="company_facts",
            content=content,
            provenance=provenance,
        )

    def from_retrieved_chunk(
        self,
        chunk: RetrievedChunk,
    ) -> Evidence:

        provenance = {
            "chunk_id": chunk.chunk_id,
            "distance": chunk.distance,
            **chunk.metadata,
        }

        return Evidence(
            source_type="filing_chunk",
            content=chunk.text,
            provenance=provenance,
        )