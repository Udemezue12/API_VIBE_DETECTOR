import logging

import httpx
from celery import shared_task

from .cache import SyncCacheDependencies
from .repo.website_scan_repo import GithubScanResultRepo
from .services.ast_analyzer import ASTAnalyzer
from .services.commit_burst import detect_commit_burst
from .services.copilot_detector import CopilotPatternDetector
from .services.docstring_detector import DocstringDetector
from .services.github_services import GithubScanner
from .services.llm_fingerprint import LLMFingerprint
from .services.readme_detector import ReadmeDetector
from .services.vibe_score import VibeScoreEngine

logger = logging.getLogger(__name__)


MAX_FILES = 200
MAX_FILE_SIZE = 50000


@shared_task(
    name="scan_repository",
    autoretry_for=(httpx.HTTPError, ConnectionError),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
    time_limit=300,
)
def scan_repository(repo_url: str):
    logger.info(f"Starting repository scan: {repo_url}")

    cache_service = SyncCacheDependencies()
    repo_storage = GithubScanResultRepo()

    key = f"github-scan:{repo_url}"

    cached = cache_service.get_from_cache(key)

    if cached:
        return cached

    try:
        github = GithubScanner()
        fingerprint = LLMFingerprint()
        doc_detector = DocstringDetector()
        copilot_detector = CopilotPatternDetector()
        readme_detector = ReadmeDetector()
        ast_analyzer = ASTAnalyzer()
        score_engine = VibeScoreEngine()

        logger.info("Fetching repository metadata")

        repo = github.get_repo(repo_url)

        logger.info("Fetching commits")
        commits = github.get_commits(repo)

        logger.info("Fetching repository files")
        files = github.get_repo_files(repo)

        burst_count = detect_commit_burst(commits)

        commit_patterns = []
        code_patterns = []
        doc_patterns = []
        readme_patterns = []
        ast_scores = []

        logger.info("Analyzing commits")

        for commit in commits:
            msg = commit.commit.message.lower()

            if "chatgpt" in msg:
                commit_patterns.append("chatgpt_commit")

            if "copilot" in msg:
                commit_patterns.append("copilot_commit")

        logger.info("Analyzing repository files")

        file_count = 0

        for file in files:
            if file_count >= MAX_FILES:
                logger.info("File scan limit reached")
                break

            try:
                if file.size > MAX_FILE_SIZE:
                    continue

                code = file.decoded_content.decode()

                code_patterns += fingerprint.detect(code)

                doc_patterns += doc_detector.detect(code)

                code_patterns += copilot_detector.detect(code)

                ast_result = ast_analyzer.analyze_code(code)

                ast_scores.append(ast_result["llm_probability"])

                file_count += 1

            except Exception as e:
                logger.warning(f"Skipping file due to error: {e}")
                continue

        

        logger.info("Analyzing README")

        try:
            readme = repo.get_readme().decoded_content.decode()

            readme_patterns = readme_detector.detect(readme)

        except Exception:
            logger.warning("README not found or unreadable")

        avg_ast_score = sum(ast_scores) / len(ast_scores) if ast_scores else 0

        vibe_score = score_engine.calculate(
            commit_patterns,
            code_patterns,
            doc_patterns,
            readme_patterns,
            burst_count,
            avg_ast_score,
        )

        signals = {
            "commit_patterns": commit_patterns,
            "code_patterns": code_patterns,
            "doc_patterns": doc_patterns,
            "readme_patterns": readme_patterns,
            "commit_burst": burst_count,
            "ast_probability": avg_ast_score,
        }

        logger.info("Saving scan result")

        created = repo_storage.sync_create(
            url=repo_url,
            vibe_score=vibe_score,
            is_vibecoded=vibe_score > 50,
            signals=signals,
        )
        

        result = {
            "repo": str(created.repo_url),
            "score": vibe_score,
            "likely_vibecoded": vibe_score > 50,
            "signals": signals,
        }

        logger.info("Caching scan result")

        cache_service.set_from_cache(key, result, timeout=1800)

        logger.info("Repository scan completed")

        return result

    except Exception as e:
        logger.error(f"Repository scan failed: {e}")

        raise
