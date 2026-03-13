from github import Github
import os
from dotenv import load_dotenv


load_dotenv()


class GithubScanner:

    def __init__(self):
        self.github_client = Github(os.getenv("GITHUB_TOKEN"))

    def scan_repo(self, repo_url: str):

        repo_name = repo_url.split("github.com/")[1]
        repo = self.github_client.get_repo(repo_name)

        commits = list(repo.get_commits()[:30])

        ai_patterns = []

        for commit in commits:

            msg = commit.commit.message.lower()

            if "chatgpt" in msg:
                ai_patterns.append("chatgpt_commit")

            if "copilot" in msg:
                ai_patterns.append("copilot_commit")

            if "ai generated" in msg:
                ai_patterns.append("ai_generated_commit")

        return {
            "commit_count": len(commits),
            "ai_commit_patterns": ai_patterns
        }
    def get_repo(self, repo_url):
        repo_name = repo_url.split("github.com/")[1]
        return self.github_client.get_repo(repo_name)

    def get_commits(self, repo):
        commits = list(repo.get_commits()[:30])
        return commits
    def get_repo_files(self, repo):

        contents = repo.get_contents("")
        files = []

        while contents:
            file_content = contents.pop(0)

            if file_content.type == "dir":
                contents.extend(repo.get_contents(file_content.path))
            else:
                if file_content.path.endswith((".py", ".js", ".ts", ".java", ".go")):
                    files.append(file_content)

        return files
