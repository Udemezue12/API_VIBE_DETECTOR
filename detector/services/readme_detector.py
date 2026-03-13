import re
from ..ai_patterns import README_PATTERNS

class ReadmeDetector:

    def detect(self, text):

        matches = []

        for pattern in README_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                matches.append(pattern)

        return matches