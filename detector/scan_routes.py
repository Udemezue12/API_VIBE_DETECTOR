

from django_bolt import BoltAPI
from django_bolt.auth import IsAuthenticated
from django_bolt.middleware import rate_limit

from .serializers import ScanSerializer
from .views import ScanView

website_api = BoltAPI(django_middleware=True)


@website_api.post(
    "/scan/website",
    status_code=200,
    summary="Website scan",
    description="Scan a website",
    tags=["Scan Website"],
    guards=[IsAuthenticated()],
)
@rate_limit(rps=3, burst=5)
async def scan_website(data: ScanSerializer):
    return await ScanView().scan_website(data=data)


@website_api.get(
    "/{url}/results/",
    summary="Website Scanned Results",
    description="Get Scanned Results",
    tags=["Scan Website"],
    guards=[IsAuthenticated()],
)
@rate_limit(rps=3, burst=5)
async def scan_github_results(url: str):
    return await ScanView().get_scan_website_result(url)


# @website_api.delete(
#     "/scan/{id}",
#     status_code=200,
#     summary="Website Delete",
#     description="Delete a website",
#     tags=["Scan Website"],
# )
# @rate_limit(rps=3, burst=5)
# async def delete(id: uuid.UUID):
#     return await ScanView().delete_scan(id)
