class VibeScoreEngine:

    def calculate(
        self,
        commit_patterns,
        code_patterns,
        docstring_patterns,
        readme_patterns,
        burst_count,
        ast_score
    ):

        score = 0

        score += len(commit_patterns) * 15
        score += len(code_patterns) * 20
        score += len(docstring_patterns) * 10
        score += len(readme_patterns) * 15
        score += burst_count * 5

        score += int(ast_score * 20)

        return min(score, 100)