"""
Pagination Parameters and Response Helper for EROMS APIs
"""
import math
from typing import TypeVar, Generic, Sequence, Optional
from pydantic import BaseModel
from fastapi import Query
from backend.app.config import settings

T = TypeVar("T")

class PaginationParams:
    def __init__(
        self,
        page: int = Query(1, ge=1, description="Page number starting at 1"),
        page_size: int = Query(settings.DEFAULT_PAGE_SIZE, ge=1, le=settings.MAX_PAGE_SIZE, description="Number of items per page"),
        search: Optional[str] = Query(None, description="Free text search term"),
        sort_by: Optional[str] = Query(None, description="Field name to sort by"),
        sort_desc: bool = Query(False, description="Sort descending if true")
    ):
        self.page = page
        self.page_size = page_size
        self.search = search.strip() if search else None
        self.sort_by = sort_by
        self.sort_desc = sort_desc

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size

class PaginatedResponse(BaseModel, Generic[T]):
    items: Sequence[T]
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_prev: bool

    @classmethod
    def create(cls, items: Sequence[T], total: int, params: PaginationParams):
        total_pages = math.ceil(total / params.page_size) if params.page_size > 0 else 1
        return cls(
            items=items,
            total=total,
            page=params.page,
            page_size=params.page_size,
            total_pages=total_pages,
            has_next=params.page < total_pages,
            has_prev=params.page > 1
        )
