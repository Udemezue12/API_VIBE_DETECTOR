import uuid

from ..enums import ScanStatus
from ..models import GithubScanResult, WebsiteScanResult
from ..repo_deps import CRUDDependencies


class ScanResultRepo:
    def __init__(self):
        self.repo_deps = CRUDDependencies()

    async def acreate(
        self,
        url: str,
        vibe_score: float,
        is_vibecoded: bool,
        detected_framework: str,
        ai_patterns,
    ) -> WebsiteScanResult:
        results = await self.repo_deps.acreate_object(
            model=WebsiteScanResult,
            vibe_score=vibe_score,
            is_vibecoded=is_vibecoded,
            ai_patterns=ai_patterns,
            detected_framework=detected_framework,
            url=url,
        )
        return results

    def create(
        self,
        url: str,
        vibe_score: float,
        is_vibecoded: bool,
        detected_framework: str,
        ai_patterns,
        status: ScanStatus
    ) -> WebsiteScanResult:
        results = self.repo_deps.create_object(
            model=WebsiteScanResult,
            vibe_score=vibe_score,
            is_vibecoded=is_vibecoded,
            ai_patterns=ai_patterns,
            detected_framework=detected_framework,
            url=url,status=status
        )
        return results

    

    async def delete(self, pk: uuid.UUID):
        return await self.repo_deps.adelete(model=WebsiteScanResult, id=pk)


class GithubScanResultRepo:
    def sync_create(
        self, url: str, vibe_score: float, is_vibecoded: bool, signals
    ) -> GithubScanResult:
        results = GithubScanResult.objects.create(
            repo_url=url,
            vibe_score=vibe_score,
            is_vibecoded=is_vibecoded,
            signals=signals,
        )

        return results
