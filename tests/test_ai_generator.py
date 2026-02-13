from app.ai_engine.content_generator import AIContentGenerator
from app.models.schemas import ProductCreate


def test_ai_generate_product_content() -> None:
    generator = AIContentGenerator()
    draft = generator.generate_product_content(
        ProductCreate(
            title="便携风扇",
            cost_price=19.9,
            sale_price=39.9,
            category="3C数码",
            keywords=["静音", "续航"],
        )
    )

    assert "高转化" in draft.optimized_title
    assert len(draft.recommended_skus) >= 1
