from business_query.src.api import fetch_query_results


def create_query(query, duration):
    # Logic for adding data in mongo

    query_answer = fetch_query_results.fetch_query_result(query, duration)

    # Logic for adding result and response code in mongo

    return query_answer
