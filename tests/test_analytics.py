from app.analytics.service import AnalyticsService


def test_analyze_sales_low_orders() -> None:
    svc = AnalyticsService()
    output = svc.analyze_sales({"data": {"orders": [{"pay_amount": 20}]}})

    assert output["order_count"] == 1
    assert "建议" in output["decision"]
