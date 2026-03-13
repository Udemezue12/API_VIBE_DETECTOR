import logging

from django_bolt.responses import Response
import httpx
from celery import shared_task

from detector.enums import ScanStatus


from .cache import SyncCacheDependencies
from .repo.website_scan_repo import ScanResultRepo
from .services.ai_analysis import DeepAIAnalysis
from .services.detect_services import DetectServices

logger = logging.getLogger(__name__)


MAX_FILES = 200
MAX_FILE_SIZE = 50000


@shared_task(
    name="scan_website",
    autoretry_for=(httpx.HTTPError, ConnectionError),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
    time_limit=300,
)
def scan_website(url: str):
    logger.info(f"Starting website scan: {url}")

    cache_service = SyncCacheDependencies()
    detect_services = DetectServices()
    repo = ScanResultRepo()

    ai_deps = DeepAIAnalysis()

    key = f"website-scan:{url}"

    cached = cache_service.get_from_cache(key)

    if cached:
        return cached

    try:
        html = detect_services.sync_fetch_website(url=url)

        if not html:
            return Response({"error": "Unable to fetch website"}, status_code=400)

        framework = detect_services.sync_detect_framework(html)
        signals = ai_deps.deep_ai_analysis(html, url)

        score = detect_services.calculate_vibe_score_signals(signals)

        created = repo.create(
            url=url,
            vibe_score=score,
            is_vibecoded=score > 50,
            detected_framework=framework,
            ai_patterns=signals,
            status=ScanStatus.SUCCESSFUL,
        )

        return {
            "url": created.url,
            "vibe_score": created.vibe_score,
            "detected_framework": created.detected_framework,
            "ai_patterns": created.ai_patterns,
        }

    except Exception as e:
        return Response({"error": str(e)}, status_code=500)
    finally:
        detect_services.sync_close()
