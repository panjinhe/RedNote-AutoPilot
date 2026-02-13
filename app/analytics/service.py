class AnalyticsService:
    def analyze_sales(self, order_payload: dict) -> dict:
        orders = order_payload.get("data", {}).get("orders", [])
        order_count = len(orders)
        gross = sum(float(o.get("pay_amount", 0)) for o in orders)

        suggestion = "维持当前策略"
        if order_count < 3:
            suggestion = "建议优化标题和首图，必要时小幅降价"
        elif order_count > 50:
            suggestion = "可测试提价 3%-5% 并加大投放"

        return {
            "order_count": order_count,
            "gross_amount": round(gross, 2),
            "decision": suggestion,
        }
