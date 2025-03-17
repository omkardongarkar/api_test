from collections import defaultdict
from datetime import datetime, timedelta

from common import constants

# Sample Data
data = [
    {"score": 82, "tmp": datetime(2023, 1, 10, 10, 0)},
    {"score": 9, "tmp": datetime(2023, 1, 20, 12, 0)},
    {"score": 6, "tmp": datetime(2023, 2, 5, 14, 0)},
    {"score": 6, "tmp": datetime(2023, 2, 25, 10, 0)},
    {"score": 6, "tmp": datetime(2023, 3, 15, 11, 0)},
    {"score": 6, "tmp": datetime(2023, 4, 20, 13, 0)},
    {"score": 6, "tmp": datetime(2024, 5, 9, 9, 0)},
    {"score": 6, "tmp": datetime(2024, 6, 10, 8, 0)},
    {"score": 6, "tmp": datetime(2024, 7, 15, 15, 0)},
    {"score": 6, "tmp": datetime(2024, 9, 1, 10, 0)},
    {"score": 6, "tmp": datetime(2024, 11, 12, 12, 0)},
    {"score": 6, "tmp": datetime(2025, 2, 20, 14, 0)},
]

def keys_for_days_interval_time_range(start_time, end_time):
    
    key=f"{start_time.strftime('%Y-%m-%d')} - {end_time.strftime('%Y-%m-%d')}"
    return key




def keys_for_days_interval_months_range(starting_month, ending_month, year):
    key= f"{year}-{starting_month:02d} - {year}-{ending_month:02d}"
    return key


def keys_for_interval_week_range(date):
    
    start_of_week = date - timedelta(days=date.weekday()) 
    end_of_week = start_of_week + timedelta(days=6)  
    key = f"{start_of_week.strftime('%Y-%m-%d')} - {end_of_week.strftime('%Y-%m-%d')}"
    return key

def get_key_for_hour(current_hour,filtered_date):
    if current_hour < 12:
               
        end_hour = start_hour + 1
    else:
        
        start_hour = (filtered_date.hour // 2) * 2  # Round down to nearest 2-hour mark
        end_hour = start_hour + 2

    key = f"{start_hour:02d}.00-{end_hour:02d}.00"
    
    return key

def get_key_for_two_days_interval(filtered_date):
    start_day = (filtered_date.day // 2) * 2 +1 # Round down to nearest multiple of 3
    end_day = start_day + 1
    key = keys_for_days_interval_time_range(
        datetime(filtered_date.year, filtered_date.month, start_day),
        datetime(filtered_date.year, filtered_date.month, min(end_day, 28))
    )
    return key

def get_key_for_three_days_interval(filtered_date):
    start_day = (filtered_date.day // 3) * 3 + 1  # Round down to nearest multiple of 3
    end_day = start_day + 2
    key = keys_for_days_interval_time_range(
        datetime(filtered_date.year, filtered_date.month, start_day),
        datetime(filtered_date.year, filtered_date.month, min(end_day, 28))
    )
    return key

def get_keys_for_ten_days_interval(filtered_date):
    start_day = (filtered_date.day // 10) * 10 + 1  
    end_day = start_day + 9
    key = keys_for_days_interval_time_range(
        datetime(filtered_date.year, filtered_date.month, start_day),
        datetime(filtered_date.year, filtered_date.month, min(end_day, 28))
    )
    return key

def get_key_for_months_interval(total_months,req_month,req_year,filtered_date):
    if total_months <= constants.MONTHLY_INTERVAL:
               
        key = filtered_date.strftime("%Y-%m")

    elif total_months <= constants.TWO_MONTHLY_INTERVAL:
        # Group by 2-month Intervals
        start_month = (req_month // 2) * 2 + 1  
        end_month = start_month + 1
        key = keys_for_days_interval_months_range(start_month, end_month, req_year)

    else:
        # Group by 3-month Intervals
        start_month = (req_month // 3) * 3 + 1  # Round down to nearest 3rd month
        end_month = start_month + 2
        key = keys_for_days_interval_months_range(start_month, end_month, req_year)
    return key

def extract_data_on_interval(items, days):
    grouped_data = defaultdict(int)  # Store sum of scores per time range
    current_hour = datetime.now().hour  # Get current hour
    try:
        for item in items:
            # print(data)
            filtered_date = item["_id"]
            score = item["total_interactions"]

            if days == constants.HOURLY_INTERVAL:
                key=get_key_for_hour(current_hour,filtered_date)

            elif days <= constants.DAILY_INTERVAL:
                # Group by Day (YYYY-MM-DD)
                key = filtered_date.strftime("%Y-%m-%d")

            elif days<=constants.TWO_DAYS_INTERVAL:
                key = get_key_for_two_days_interval(filtered_date)
                


            elif days <= constants.THREE_DAYS_INTERVAL:
                #  
                key=get_key_for_three_days_interval(filtered_date)


            elif days <= constants.WEEKLY_INTERVAL:
                # Group by Week (YYYY-MM-DD - YYYY-MM-DD)
                key = keys_for_interval_week_range(filtered_date)

            elif days <= constants.TEN_DAYS_INTERVAL:
                # Group by 10-day Intervals
                key = get_keys_for_ten_days_interval(filtered_date)

            else:
                # Convert to months for long-term grouping
                total_months = days // 30  # Approximate number of months
                req_month = filtered_date.month
                req_year = filtered_date.year

                key = get_key_for_months_interval(total_months,req_month,req_year,filtered_date)

                

            grouped_data[key] += score  # Sum up the scores

    except Exception as e:
        print("error is: ",e)

    return dict(grouped_data)


def group_data_by_time1(data, days):
    grouped_data = defaultdict(lambda: defaultdict(int))  # { "r1": { "time_range": total_count }, ... }
    current_hour = datetime.now().hour

    
    for entry in data:
        for key, values in entry.items():  # Loop through r1, r2, etc.
            for item in values:
                filtered_date = item["_id"]
                score = item["total_interactions"]
                if days == constants.HOURLY_INTERVAL:
                    key=get_key_for_hour(current_hour,filtered_date)

                elif days <= constants.DAILY_INTERVAL:
                    # Group by Day (YYYY-MM-DD)
                    key = filtered_date.strftime("%Y-%m-%d")

                elif days<=constants.TWO_DAYS_INTERVAL:
                    key = get_key_for_two_days_interval(filtered_date)
                    


                elif days <= constants.THREE_DAYS_INTERVAL:
                    #  
                    key=get_key_for_three_days_interval(filtered_date)


                elif days <= constants.WEEKLY_INTERVAL:
                    # Group by Week (YYYY-MM-DD - YYYY-MM-DD)
                    key = keys_for_interval_week_range(filtered_date)

                elif days <= constants.TEN_DAYS_INTERVAL:
                    # Group by 10-day Intervals
                    key = get_keys_for_ten_days_interval(filtered_date)

                else:
                    # Convert to months for long-term grouping
                    total_months = days // 30  # Approximate number of months
                    req_month = filtered_date.month
                    req_year = filtered_date.year

                    key = get_key_for_months_interval(total_months,req_month,req_year,filtered_date)

                    

        grouped_data[key] = score  # Sum up the scores

    return dict(grouped_data)




# Example usage
days = 125 # Change this to test different cases
grouped_result = extract_data_on_interval(data, days)

# Print grouped results
for key, total_score in grouped_result.items():
    print(f"Group: {key} → Total Score: {total_score}")
