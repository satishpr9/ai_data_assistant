from sqlalchemy import create_engine
import pandas as pd
from app.vectorstore import add_texts

username = "root"
password = ""
host = "localhost"
port = "3306"
database = "ai_data_asistant"

DATABASE_URL = f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}"

def ingest_business_data():
    engine = create_engine(DATABASE_URL)
    df = pd.read_sql("SELECT * FROM business_data", engine)

    texts = []
    metadatas = []

    for _, row in df.iterrows():
        text = (
            f"Customer {row.customer_name} made a {row.finance_type} "
            f"purchase of {row.product} worth {row.amount} "
            f"in {row.month}. Sales count: {row.quantity}."
        )

        texts.append(text)
        metadatas.append({
            "source": "mysql",
            "table": "business_data",
            "customer": row.customer_name,
            "month": row.month,
            "finance": row.finance_type
        })

    add_texts(texts=texts, metadatas=metadatas)
    return len(texts)