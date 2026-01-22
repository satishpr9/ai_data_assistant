def is_chart_query(query:str)->bool:
    keywords=[
        "chart","graph","plot",
        "show","trend","visualize",

    ]


    return any(k in query.lower() for k in keywords)

def is_aggregation_query(query: str) -> bool:
    keywords = [
        "most", "total", "sum", "highest",
        "maximum", "max", "spent","Which"
    ]
    return any(k in query.lower() for k in keywords)
