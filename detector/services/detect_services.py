import re
from collections import Counter

import httpx
from bs4 import BeautifulSoup

from ..ai_patterns import AI_PATTERNS, COMMON_AI_HTML_PATTERNS


class DetectServices:
    def __init__(self):
        self.async_client = httpx.AsyncClient(timeout=10)
        self.sync_client = httpx.Client(timeout=10)

    async def async_fetch_website(self, url):
        try:
            response = await self.async_client.get(url)
            if response.status_code >= 400:
                return None
            return response.text
        except httpx.HTTPError:
            return None

    def sync_fetch_website(self, url: str) -> str | None:
        try:
            response = self.sync_client.get(url)
            response.raise_for_status()
            return response.text
        except httpx.HTTPError:
            return None

    def fetch_js_bundles(self, bundles, base_url):
        js_contents = []

        for bundle in bundles:
            try:
                if bundle.startswith("http"):
                    url = bundle
                else:
                    url = base_url.rstrip("/") + "/" + bundle.lstrip("/")

                resp = self.sync_client.get(url)

                if resp.status_code == 200:
                    js_contents.append(resp.text)

            except Exception:
                continue

        return js_contents

    def sync_close(self):
        self.sync_client.close()

    async def async_close(self):
        await self.async_client.aclose()

    async def async_detect_framework(self, html):
        if "next.js" in html:
            return "Next.js"

        if "react" in html:
            return "React"

        if "vue" in html:
            return "Vue"

        if "django" in html:
            return "Django"

        return "Unknown"

    def sync_detect_framework(self, html):
        soup = BeautifulSoup(html, "html.parser")

        scripts = [s.get("src", "") for s in soup.find_all("script")]

        html_lower = html.lower()

        if "__next" in html_lower or "_next/static" in html_lower:
            return "Next.js"

        if any("react" in s for s in scripts) or "data-reactroot" in html_lower:
            return "React"

        if "vue" in html_lower or "data-v-" in html_lower:
            return "Vue"

        if "ng-version" in html_lower:
            return "Angular"

        if "csrfmiddlewaretoken" in html_lower:
            return "Django"

        if "laravel" in html_lower or "csrf-token" in html_lower:
            return "Laravel"

        return "Unknown"

    def detect_ai_patterns(self, html):
        matches = []

        for pattern in AI_PATTERNS:
            if re.search(pattern, html, re.IGNORECASE):
                matches.append(pattern)

        return matches

    def detect_ai_structure(self, html: str):
        indicators = []

        soup = BeautifulSoup(html, "html.parser")

        inline_styles = soup.find_all(style=True)

        if len(inline_styles) > 20:
            indicators.append("excessive_inline_styles")

        class_patterns = re.findall(r"class=\"([^\"]+)\"", html)

        if len(class_patterns) > 50:
            indicators.append("high_class_density")

        if html.count("container") > 20:
            indicators.append("repeated_layout_pattern")

        return indicators

    def calculate_vibe_score(self, html):
        score = 0

        ai_patterns = self.detect_ai_patterns(html)
        structure_patterns = self.detect_ai_structure(html)

        score += len(ai_patterns) * 25

        score += len(structure_patterns) * 15

        for pattern in COMMON_AI_HTML_PATTERNS:
            if pattern in html:
                score += 10

        score = min(score, 100)

        signals = {"ai_patterns": ai_patterns, "structure_patterns": structure_patterns}

        return score, signals

    def calculate_vibe_score_signals(self, signals):
        score = 0

        score += len(signals["fingerprints"]) * 25

        score += len(signals["ast"]) * 5

        score += len(signals["entropy"]) * 15

        score += len(signals["repetition"]) * 5

        score += len(signals["bundles"]) * 5

        return min(score, 100)

    def extract_js_bundles(self, html):
        soup = BeautifulSoup(html, "html.parser")

        scripts = soup.find_all("script")

        bundles = []

        for script in scripts:
            src = script.get("src")

            if src and ("static" in src or "bundle" in src or ".js" in src):
                bundles.append(src)

        return bundles

    def detect_repetition(self, code):
        tokens = re.findall(r"[a-zA-Z_]{3,}", code.lower())

        counts = Counter(tokens)

        repeated = [token for token, count in counts.items() if count > 15]

        return repeated
