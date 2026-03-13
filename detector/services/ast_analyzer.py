import ast
import math
import re
from collections import Counter

import esprima


class ASTAnalyzer:
    def analyze_code(self, code):
        results = {
            "gpt_variable_patterns": 0,
            "indent_entropy": 0,
            "llm_probability": 0,
        }

        try:
            tree = ast.parse(code)
        except Exception:
            return results

        variables = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                variables.append(node.id)

        gpt_pattern = re.compile(r"(data|result|value|response|item)_?\d*")

        matches = [v for v in variables if gpt_pattern.match(v)]

        results["gpt_variable_patterns"] = len(matches)

        lines = code.split("\n")

        indents = [len(line) - len(line.lstrip()) for line in lines if line.strip()]

        if indents:
            entropy = -sum(
                (indents.count(i) / len(indents))
                * math.log2(indents.count(i) / len(indents))
                for i in set(indents)
            )
            results["indent_entropy"] = entropy

        results["llm_probability"] = (
            results["gpt_variable_patterns"] * 0.2 + results["indent_entropy"] * 0.3
        )

        return results

    def analyze_js_ast(self, js_code):
        signals = []

        try:
            tree = esprima.parseScript(js_code)

            for node in tree.body:
                node_type = type(node).__name__

                if node_type == "FunctionDeclaration":
                    signals.append("function_decl")

                if node_type == "VariableDeclaration":
                    signals.append("var_decl")

        except Exception:
            pass

        return signals

    def calculate_entropy(self, text):
        if not text:
            return 0

        counter = Counter(text)

        length = len(text)

        entropy = 0

        for count in counter.values():
            p = count / length

            entropy -= p * math.log2(p)

        return entropy
