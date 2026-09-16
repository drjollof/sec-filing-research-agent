import re
from dataclasses import dataclass, field


@dataclass
class Claim:
    text: str
    claim_type: str
    evidence_ids: list[str] = field(default_factory=list)


class ClaimExtractor:
    """
    Deterministically breaks a generated answer into atomic,
    independently verifiable claims.
    """

    EVIDENCE_ID_PATTERN = re.compile(
        r"(?:\[|【|\()E(\d+)(?:\]|】|\))", 
        re.IGNORECASE
    )

    NUMERIC_CLAIM_PATTERN = re.compile(
        r"""
        (?:
            \$\s*
            (?:\d{1,3}(?:,\d{3})+|\d+(?:\.\d+)?)
            (?:\.\d+)?
            \s*
            (?:trillion|billion|million|thousand)?
        )
        |
        (?:
            (?:\d{1,3}(?:,\d{3})+|\d+(?:\.\d+)?)
            \s*
            (?:trillion|billion|million|thousand)
        )
        |
        (?:
            \d+(?:\.\d+)?
            \s*%
        )
        """,
        re.IGNORECASE | re.VERBOSE,
    )

    def extract(self, answer: str) -> list[Claim]:
        if not answer or not answer.strip():
            return []

        claims = []


        for block in self._split_blocks(answer):
            block = block.strip()

            if not block:
                continue

            if self._is_framing_noise(block):
                continue

            evidence_ids = self._extract_evidence_ids(block)
            claim_text = self._clean_text(block)

            if not claim_text:
                continue
            claim_type = self._determine_type(claim_text)

            claims.append(
                Claim(
                    text=claim_text,
                    claim_type=claim_type,
                    evidence_ids=evidence_ids,
                )
            )

        return claims

    def _split_blocks(self, text: str) -> list[str]:
        return [
            block.strip()
            for block in re.split(r"\n+", text)
            if block.strip()
        ]

    def _clean_text(self, text: str) -> str:
        text = self.EVIDENCE_ID_PATTERN.sub("", text)
        text = re.sub(r"[\*|#-]", "", text)
        return re.sub(r"\s+", " ", text).strip()

    def _extract_evidence_ids(self, text: str) -> list[str]:
        matches = self.EVIDENCE_ID_PATTERN.findall(text)
        seen = set()
        ids = []
        for m in matches:
            eid = f"E{m}"
            if eid not in seen:
                seen.add(eid)
                ids.append(eid)
        return ids

    def _determine_type(self, text: str) -> str:
        for match in self.NUMERIC_CLAIM_PATTERN.finditer(text):
            val = match.group(0).strip()
            if not re.fullmatch(r"(19|20)\d{2}", val):
                return "numeric"
        return "narrative"

    def _is_framing_noise(self, text: str) -> bool:
        normalized = text.lower().replace(" ", "")
        noise_phrases = [
            "basedontheprovidedevidence",
            "accordingtothefiling",
            "theansweristherefore",
            "icannotanswerthisbasedontheprovidedevidence",
            "hereistheinformation",
            "appleidentifiesthefollowing",
            "thefollowingrisks",
        ]
        
        for phrase in noise_phrases:
            if phrase in normalized and len(normalized) < len(phrase) + 15:
                return True
                
        if len(text.split()) < 8 and not self.EVIDENCE_ID_PATTERN.search(text):
            return True
            
        return False