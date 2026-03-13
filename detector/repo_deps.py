from typing import Optional, Type, TypeVar

from django.db import IntegrityError
from django.db.models import Model
from django_bolt.exceptions import HTTPException

T = TypeVar("T", bound=Model)


class ExistingDependencies:
    async def async_check_existing(
        self, model: Type[T], raise_error_if_exists=True, error_field="Record", **kwargs
    ):
        obj = await model.objects.filter(**kwargs).aexists()
        if raise_error_if_exists and obj:
            raise HTTPException(
                status_code=409, detail=f"{error_field} already exists."
            )
        if not raise_error_if_exists and not obj:
            raise HTTPException(status_code=404, detail=f"{error_field} not found.")
        return obj


class CRUDDependencies:
    def get_object(self, model: Type[T], **filters) -> Optional[T]:
        try:
            return model.objects.get(**filters)
        except model.DoesNotExist:
            return None

    async def aget_object(self, model: Type[T], **filters) -> Optional[T]:
        try:
            return await model.objects.aget(**filters)
        except model.DoesNotExist:
            return None

    def create_object(self, model: Type[T], **data) -> T:
        return model.objects.create(**data)

    async def acreate_object(self, model: Type[T], **data) -> T:
        try:
            return await model.objects.acreate(**data)
        except IntegrityError:
            return None

    # async def acreate_object(self, model: Type[T], **data) -> T:

    #     obj = model(**data)
    #     await obj.asave()
    #     return obj

    def get_or_create(self, model: Type[T], defaults=None, **filters) -> tuple[T, bool]:
        return model.objects.get_or_create(defaults=defaults or {}, **filters)

    async def aget_or_create(
        self, model: Type[T], defaults=None, **filters
    ) -> tuple[T, bool]:
        return await model.objects.aget_or_create(defaults=defaults or {}, **filters)

    def count(self, model: Type[T], **filters) -> int:
        queryset = model.objects.filter(**filters) if filters else model.objects.all()
        return queryset.count()

    async def acount(self, model: Type[T], **filters) -> int:
        queryset = model.objects.filter(**filters) if filters else model.objects.all()
        return await queryset.acount()

    def exists(self, model: Type[T], **filters) -> bool:
        return model.objects.filter(**filters).exists()

    async def aexists(self, model: Type[T], **filters) -> bool:
        return await model.objects.filter(**filters).aexists()

    def get_list(
        self,
        model: Type[T],
        select_related: list[str] | None = None,
        prefetch_related: list[str] | None = None,
        limit: int | None = None,
        **filters,
    ) -> list[T]:
        queryset = model.objects.filter(**filters)

        if select_related:
            queryset = queryset.select_related(*select_related)

        if prefetch_related:
            queryset = queryset.prefetch_related(*prefetch_related)

        if limit:
            queryset = queryset[:limit]

        return list(queryset)

    async def aget_list(
        self,
        model: Type[T],
        select_related: list[str] | None = None,
        prefetch_related: list[str] | None = None,
        limit: int | None = None,
        **filters,
    ) -> list[T]:
        queryset = model.objects.filter(**filters)

        if select_related:
            queryset = queryset.select_related(*select_related)

        if prefetch_related:
            queryset = queryset.prefetch_related(*prefetch_related)

        if limit:
            queryset = queryset[:limit]

        return [obj async for obj in queryset]

    def update(self, model: Type[T], filters: dict, updates: dict) -> int:
        return model.objects.filter(**filters).update(**updates)

    async def aupdate(self, model: Type[T], filters: dict, updates: dict) -> int:
        return await model.objects.filter(**filters).aupdate(**updates)

    def delete(self, model: Type[T], **filters) -> int:
        deleted_count, _ = model.objects.filter(**filters).delete()
        return deleted_count

    async def adelete(self, model: Type[T], **filters) -> int:
        deleted_count, _ = await model.objects.filter(**filters).adelete()
        return deleted_count
