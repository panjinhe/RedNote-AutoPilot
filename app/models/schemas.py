from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4


class ProductStatus(str, Enum):
    online = "online"
    offline = "offline"


class TaskStatus(str, Enum):
    drafted = "drafted"
    running = "running"
    done = "done"
    failed = "failed"


@dataclass
class ProductBase:
    title: str
    cost_price: float
    sale_price: float
    category: str
    keywords: list[str] = field(default_factory=list)


@dataclass
class ProductCreate(ProductBase):
    pass


@dataclass
class ProductRecord(ProductBase):
    id: str = ""
    xhs_product_id: str | None = None
    status: ProductStatus = ProductStatus.offline


@dataclass
class AIProductDraft:
    optimized_title: str
    bullet_points: list[str]
    detail_copy: str
    tags: list[str]
    faq: list[str]
    recommended_skus: list[str]

    def model_dump(self) -> dict:
        return {
            "optimized_title": self.optimized_title,
            "bullet_points": self.bullet_points,
            "detail_copy": self.detail_copy,
            "tags": self.tags,
            "faq": self.faq,
            "recommended_skus": self.recommended_skus,
        }


@dataclass
class ListingPack:
    product_id: str
    title: str
    desc: str
    tags: list[str]
    sale_price: float
    cost_price: float
    sku_list: list[dict[str, str | int]]
    images: list[str] = field(default_factory=list)
    checklist: list[str] = field(default_factory=list)
    version: str = "v1"

    def model_dump(self) -> dict:
        return {
            "product_id": self.product_id,
            "title": self.title,
            "desc": self.desc,
            "tags": self.tags,
            "sale_price": self.sale_price,
            "cost_price": self.cost_price,
            "sku_list": self.sku_list,
            "images": self.images,
            "checklist": self.checklist,
            "version": self.version,
        }


@dataclass
class ListingTask:
    task_id: str
    product_id: str
    status: TaskStatus
    listing_pack_version: str
    input_snapshot: dict
    channel: str
    created_at: str
    updated_at: str
    output: dict = field(default_factory=dict)

    @classmethod
    def create(cls, product_id: str, listing_pack_version: str, input_snapshot: dict, channel: str) -> "ListingTask":
        now = datetime.now(timezone.utc).isoformat()
        return cls(
            task_id=str(uuid4()),
            product_id=product_id,
            status=TaskStatus.drafted,
            listing_pack_version=listing_pack_version,
            input_snapshot=input_snapshot,
            channel=channel,
            created_at=now,
            updated_at=now,
            output={},
        )

    def model_dump(self) -> dict:
        return {
            "task_id": self.task_id,
            "product_id": self.product_id,
            "status": self.status.value,
            "listing_pack_version": self.listing_pack_version,
            "input_snapshot": self.input_snapshot,
            "channel": self.channel,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "output": self.output,
        }
