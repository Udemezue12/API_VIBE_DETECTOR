
from datetime import datetime

from django.contrib.auth import get_user_model

from ..models import BlacklistedToken
from ..repo_deps import CRUDDependencies

User = get_user_model()


class AuthRepo:
    def __init__(self):
        self.repo_deps = CRUDDependencies()
    async def get_user_email(self, email:str)-> User | None:
        email_payload = email.strip().lower()
        return await self.repo_deps.aget_object(email=email_payload)
    async def blacklist_token(self, token:str) ->BlacklistedToken:
        results = await self.repo_deps.acreate_object(model=BlacklistedToken, token=token)
        return results
    async def is_token_blacklisted(self, token: str) -> bool:
      return await self.repo_deps.aexists(model=BlacklistedToken, token=token)
    def delete_expired_blacklisted_tokens(self, cutoff: datetime):
        return self.repo_deps.delete(model=BlacklistedToken, blacklisted_on_lt=cutoff)
