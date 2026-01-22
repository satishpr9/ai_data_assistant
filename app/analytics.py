from sqlalchemy import  create_engine,text

username = "root"
password = ""
host = "localhost"
port = "3306"
database = "ai_data_asistant"

DATABASE_URL = f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}"
engine=create_engine(DATABASE_URL)

def sales_by_month():
    query = """
        SELECT month, SUM(amount) AS total_sales
        FROM business_data
        GROUP BY month;

    """

    with engine.connect() as conn:
        rows = conn.execute(text(query)).fetchall()

    if not rows:
        return {
            "type": "bar",
            "labels": [],
            "datasets": []
        }

    labels = [row[0] for row in rows]
    values = [float(row[1]) for row in rows]

    return {
        "type": "bar",
        "labels": labels,
        "datasets": [
            {
                "label": "Sales by Month",
                "data": values
            }
        ]
    }

def top_customer():
    query = """
        SELECT customer_name, SUM(amount) AS total_spent
        FROM business_data
        GROUP BY customer_name
        ORDER BY total_spent DESC
        LIMIT 1;

    """
    with engine.connect() as conn:
        row = conn.execute(text(query)).fetchone()

    return {
        "answer": f"{row[0]} spent the most with a total of {float(row[1])}.",
        "sources": [
            {
                "source": "mysql",
                "table": "business_data",
                "aggregation": "SUM(amount) GROUP BY customer_name"
            }
        ]
    }
