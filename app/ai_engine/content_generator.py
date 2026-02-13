from __future__ import annotations

from app.models.schemas import AIProductDraft, ProductCreate


class AIContentGenerator:
    """MVP AI generator.

    生产可替换为 OpenAI / 本地 LLM。
    """

    def generate_product_content(self, product: ProductCreate) -> AIProductDraft:
        base_title = f"{product.category} | {product.title}"
        return AIProductDraft(
            optimized_title=f"{base_title}｜高转化优化版",
            bullet_points=[
                "精选材质，耐用且易维护",
                "适配目标人群，突出核心使用场景",
                f"成本 {product.cost_price:.2f}，建议售价 {product.sale_price:.2f}",
            ],
            detail_copy=(
                f"这是一款面向{product.category}场景打造的商品，"
                "主打高性价比与稳定品质。"
            ),
            tags=list(dict.fromkeys(product.keywords + [product.category, "高性价比"])),
            faq=[
                "Q: 发货时效？ A: 默认 24 小时内发出。",
                "Q: 支持退货吗？ A: 支持七天无理由。",
            ],
            recommended_skus=["标准版", "升级版"],
        )
