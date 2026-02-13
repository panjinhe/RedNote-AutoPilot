from dataclasses import dataclass, field
from enum import Enum


class ProductStatus(str, Enum):
    online = "online"
    offline = "offline"


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
