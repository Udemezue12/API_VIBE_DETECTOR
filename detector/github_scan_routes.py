from django_bolt import BoltAPI
from django_bolt.auth import IsAuthenticated
from django_bolt.middleware import rate_limit

from .serializers import ScanSerializer
from .views import ScanView

github_api = BoltAPI(django_middleware=True)


@github_api.post(
    "/scan/github_repo",
    summary="Github Repo scan",
    description="Scan Github repo",
    tags=["Scan Github"],
    guards=[IsAuthenticated()],
)
@rate_limit(rps=3, burst=5)
async def scan_github(data: ScanSerializer):
    return await ScanView().scan_github_repo(data=data)


@github_api.get(
    "/{repo_url}/scan_results/",
    summary="Github Repo Scanned Results",
    description="Get Scanned Results",
    tags=["Scan Github"],
    guards=[IsAuthenticated()],
)
@rate_limit(rps=3, burst=5)
async def scan_github_results(repo_url: str):
    return await ScanView().get_github_scan_result(repo_url)
