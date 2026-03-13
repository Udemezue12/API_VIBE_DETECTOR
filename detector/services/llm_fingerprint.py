import re

from ..ai_patterns import AI_SIGNATURES, LLM_FINGERPRINTS


class LLMFingerprint:
    def detect(self, text):
        matches = []

        for pattern in AI_SIGNATURES:
            if re.search(pattern, text, re.IGNORECASE):
                matches.append(pattern)

        return matches

    def detect_llm_fingerprints(self, code):
        matches = []

        for pattern in LLM_FINGERPRINTS:
            if re.search(pattern, code, re.IGNORECASE):
                matches.append(pattern)

        return matches
