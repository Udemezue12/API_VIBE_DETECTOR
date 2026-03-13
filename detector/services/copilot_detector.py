class CopilotPatternDetector:

    def detect(self, code):

        matches = []

        if "def main()" in code:
            matches.append("copilot_main_pattern")

        if "if __name__ == '__main__':" in code:
            matches.append("copilot_entrypoint")

        if "async def" in code and "await" in code:
            matches.append("copilot_async_pattern")

        return matches