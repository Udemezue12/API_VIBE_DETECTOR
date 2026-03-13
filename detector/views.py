import uuid

from django.shortcuts import render
from django_bolt.exceptions import HTTPException
from django_bolt.responses import Response

from detector.enums import ScanStatus
from detector.services.ai_analysis import DeepAIAnalysis
from vibe_detector.celery_app import app as task_app

from .cache import AsyncCacheDependencies
from .models import GithubScanResult, WebsiteScanResult
from .repo.website_scan_repo import ScanResultRepo
from .repo_deps import CRUDDependencies
from .services.detect_services import DetectServices


class ScanView:
    def __init__(self):
        self.detect_services = DetectServices()
        self.repo = ScanResultRepo()
        self.cache_service = AsyncCacheDependencies()
        self.crud_deps = CRUDDependencies()
        self.ai_deps = DeepAIAnalysis()


    
    async def scan_website(self, data):
        created = await self.crud_deps.aget_object(model=WebsiteScanResult, url=data.url)
        if created.status == ScanStatus.SUCCESSFUL:
            raise HTTPException(403, "Already Scanned")
        task_app.send_task("scan_website", args=[str(data.url)])

        return Response({"status": "Processing"})
    async def scan_github_repo(self, data):
        created = await self.crud_deps.aget_object(model=GithubScanResult, url=data.url)
        if created.status == ScanStatus.SUCCESSFUL:
            raise HTTPException(403, "Already Scanned")
        task_app.send_task("scan_repository", args=[str(data.url)])

        return Response({"status": "Processing"})
    async def delete_scan(self, pk: uuid.UUID):
        await self.repo.delete(pk)
        return {"status": 200, "message": "Deleted"}

    async def get_scan_website_result(self, url: str):
        key = f"website-scan:{url}"

        cached = await self.cache_service.get_from_cache(key)
        if cached:
            return {"status": "done", "result": cached}
        created = await self.crud_deps.aget_object(model=WebsiteScanResult, url=url)
        if not created:
            raise HTTPException(404, "Not found or Still Processing")
        result = {
            "repo": str(created.url),
            "score": str(created.vibe_score),
            "likely_vibecoded": created.vibe_score > 50,
            "signals": created.ai_patterns,
            "framework": created.detected_framework,
        }
        await self.cache_service.set_from_cache(key, result, timeout=1800)
        return result

    

    async def get_github_scan_result(self, repo_url: str):
        key = f"github-scan:{repo_url}"

        cached = await self.cache_service.get_from_cache(key)
        if cached:
            return {"status": "done", "result": cached}
        created = await self.crud_deps.aget_object(
            model=GithubScanResult, repo_url=repo_url
        )
        if not created:
            raise HTTPException(404, "Not found or Still Processing")
        result = {
            "repo": str(created.repo_url),
            "score": str(created.vibe_score),
            "likely_vibecoded": created.vibe_score > 50,
            "signals": created.signals,
        }
        await self.cache_service.set_from_cache(key, result, timeout=1800)
        return result
