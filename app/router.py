from app.analytics import top_customer,sales_by_month
def handle_chart_query(query: str):
    q = query.lower()

    month_keywords = ["month", "monthly", "per month"]
    customer_keywords = ["customer", "client", "buyer"]

    if any(k in q for k in month_keywords):
        return sales_by_month()

    if any(k in q for k in customer_keywords):
        return top_customer()

    return {
        "error": "Chart type not supported"
    }

