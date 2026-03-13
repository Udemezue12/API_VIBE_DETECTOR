import logging

from django_bolt import BoltAPI, OpenAPIConfig
from django_bolt.shortcuts import render

from .auth_routes import api as auth_api
from .csrf_token import api as csrf_api
from .github_scan_routes import github_api
from .scan_routes import website_api

logger = logging.getLogger(__name__)
api = BoltAPI(
    django_middleware=True,
    openapi_config=OpenAPIConfig(
        title="AI-Generated Code Detection API",
        version="1.0.0",
        description="Detect AI-generated code patterns in repositories",
        
    )
    
)


@api.get("/")
async def index(request):
    return render(request, "index.html")


api.mount("/api/v1", csrf_api)
api.mount("/api/v1", auth_api)
api.mount("/api/v1", website_api)
api.mount("/api/v1", github_api)
