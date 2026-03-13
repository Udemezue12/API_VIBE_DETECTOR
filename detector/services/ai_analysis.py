from .ast_analyzer import ASTAnalyzer
from .detect_services import DetectServices
from .llm_fingerprint import LLMFingerprint


class DeepAIAnalysis:
    def __init__(self):
        self.extract = DetectServices()
        self.analyzer = ASTAnalyzer()
        self.llm = LLMFingerprint()

    def deep_ai_analysis(self, html, base_url):
        signals = {
            "bundles": [],
            "ast": [],
            "entropy": [],
            "repetition": [],
            "fingerprints": [],
        }

        bundles = self.extract.extract_js_bundles(html)

        js_files = self.extract.fetch_js_bundles(bundles, base_url)

        for js in js_files:
            signals["ast"] += self.analyzer.analyze_js_ast(js)

            entropy = self.analyzer.calculate_entropy(js)

            if entropy > 4.5:
                signals["entropy"].append(entropy)

            signals["repetition"] += self.extract.detect_repetition(js)

            signals["fingerprints"] += self.llm.detect_llm_fingerprints(js)

        return signals
