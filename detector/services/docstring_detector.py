import re
from ..ai_patterns import DOCSTRING_PATTERNS

class DocstringDetector:

    def detect(self, code):

        matches = []

        for pattern in DOCSTRING_PATTERNS:
            if re.search(pattern, code, re.IGNORECASE):
                matches.append(pattern)

        return matches