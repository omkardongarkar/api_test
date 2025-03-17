from pymongo import MongoClient
from datetime import datetime, timedelta
from common import constants
from common.database import interactions_collection

client = MongoClient("mongodb://localhost:27017")
db = client["Chatsee"]
collection = db["interactions"]

async def get_last_date_and_total_days():




    pipeline = [
        {"$sort": {constants.DB_DATE_FIELD: 1}},  # Sort in descending order
        {"$limit": 1},  # Get the latest date
        {
            "$project": {
                "last_date": f"${constants.DB_DATE_FIELD}",
                "days_diff": {
                    "$dateDiff": {
                        "startDate": f"${constants.DB_DATE_FIELD}",
                        "endDate": datetime.utcnow(),
                        "unit": "day"
                    }
                }
            }
        }
    ]

    result = list(collection.aggregate(pipeline))

    if result:
        last_date = result[0]["last_date"]
        days_diff = result[0]["days_diff"]
        print(f"Last Date: {last_date}, Days Difference: {days_diff} days")
    else:
        print("No data found")

    return last_date,days_diff

def get_days_difference(days):
    today = datetime.today()
    last_day = today - timedelta(days=days)
    return last_day




if __name__ == "__main__":
    import asyncio
    asyncio.run(get_last_date_and_total_days())
    print(get_days_difference(45))