"""
Known Misinformation Patterns Heuristics

Provides instant verdict for well-documented false claims when
external APIs are unavailable.
"""

import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class MisinformationMatch:
    """Result of matching a claim against known patterns."""
    claim_type: str
    score: int
    classification: str
    confidence: str
    verdict: str
    source_note: str
    evidence: List[str]


class MisinformationHeuristics:
    """
    Heuristics for detecting well-known misinformation patterns.
    Used as fallback when API keys are not configured.
    """

    KNOWN_PATTERNS: List[Tuple] = [
        (
            r'earth is flat',
            'false',
            5,
            'Likely Fake',
            'High',
            'FALSE: The Earth is an oblate spheroid, confirmed by NASA and centuries of scientific evidence.',
            'NASA, global scientific consensus',
            [
                'NASA satellite imagery shows Earth curvature',
                'GPS systems depend on Earth spherical shape',
                'Ship hulls disappear bottom-first over horizon'
            ]
        ),
        (
            r'vaccines cause autism',
            'false',
            5,
            'Likely Fake',
            'High',
            'FALSE: No causal link between vaccines and autism. The Wakefield study was fraudulent.',
            'CDC, WHO, Lancet retraction',
            [
                'Wakefield study was fraudulent and retracted',
                '10+ studies with millions of children find no link',
                'Vaccines save millions of lives annually'
            ]
        ),
        (
            r'5g causes covid',
            'false',
            3,
            'Likely Fake',
            'High',
            'FALSE: COVID-19 is caused by a virus, not 5G radiation.',
            'WHO, scientific consensus',
            [
                'Viruses cannot be transmitted via electromagnetic waves',
                'COVID spread in areas without 5G',
                'WHO states 5G does not spread COVID'
            ]
        ),
        (
            r'moon landing (is |was )?(fake|hoax)',
            'false',
            8,
            'Likely Fake',
            'High',
            'FALSE: Moon landings (1969-1972) are documented historical facts.',
            'NASA, physical samples, independent verification',
            [
                '382 kg of lunar rocks returned to Earth',
                'Retroreflectors on Moon still used for laser ranging',
                'Soviet Luna probes tracked Apollo missions'
            ]
        ),
    ]

    def __init__(self):
        """Compile regex patterns for efficiency."""
        self._compiled_patterns = []
        for pattern_data in self.KNOWN_PATTERNS:
            pattern = pattern_data[0]
            try:
                compiled = re.compile(pattern, re.IGNORECASE)
                self._compiled_patterns.append((compiled,) + pattern_data[1:])
            except re.error as e:
                print(f"Warning: Failed to compile pattern '{pattern}': {e}")

    def check_claim(self, claim: str) -> Optional[MisinformationMatch]:
        """
        Check if a claim matches known misinformation patterns.
        """
        if not claim:
            return None

        claim_lower = claim.lower()

        for compiled_pattern in self._compiled_patterns:
            pattern = compiled_pattern[0]
            if pattern.search(claim_lower):
                return MisinformationMatch(
                    claim_type=compiled_pattern[1],
                    score=compiled_pattern[2],
                    classification=compiled_pattern[3],
                    confidence=compiled_pattern[4],
                    verdict=compiled_pattern[5],
                    source_note=compiled_pattern[6],
                    evidence=compiled_pattern[7]
                )

        return None

    def get_heuristic_verdict(self, claim: str) -> Optional[Dict]:
        """
        Get a complete heuristic verdict for a claim.
        """
        match = self.check_claim(claim)

        if match:
            return {
                'matched': True,
                'claim_type': match.claim_type,
                'score': match.score,
                'classification': match.classification,
                'confidence': match.confidence,
                'verdict': match.verdict,
                'source_note': match.source_note,
                'evidence': match.evidence,
                'is_heuristic': True,
                'api_used': False
            }

        return None


_heuristics_instance = None


def get_misinformation_heuristics() -> MisinformationHeuristics:
    """Get the global MisinformationHeuristics instance."""
    global _heuristics_instance
    if _heuristics_instance is None:
        _heuristics_instance = MisinformationHeuristics()
    return _heuristics_instance