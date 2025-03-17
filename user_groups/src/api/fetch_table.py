

from datetime import datetime, timedelta
import json
from common.constants import VIEW_CREATE_CONSTANT_STRING
from user_groups.src.models.schemas import UserGroupTable
from user_groups.src.utils.aggregation_query import get_all_users_and_interaction_count
from utils.find_last_date_and import get_days_difference


async def get_view_data(db,view_name):
    db_view_name= str(VIEW_CREATE_CONSTANT_STRING + view_name).strip()
    
    cursor = db[db_view_name].find({})
    
    data = await cursor.to_list(length=100)
    

    
    return data

async def count_all_users_interactions(records,last_day):
     

    all_users_count, unique_users_counts, total_interactions = (
            sum(
                record.get(field)
                for record in records[0]["data"]
                if record.get("_id") >= last_day
            )
            for field in ["all_users_count", "unique_users_counts", "total_interactions"]
        )
    return all_users_count, unique_users_counts, total_interactions


def get_ids_of_interaction_and_user(records,last_day):
    all_interaction_ids = []
    all_user_ids = []
    for record in records[0]["data"]:
        
        if record.get("_id") >= last_day:
            all_interaction_ids.extend(record.get("interaction_ids"))
            all_user_ids.extend(record.get("user_ids"))
            print(record)

    return all_interaction_ids,all_user_ids


async def get_table_data(groups,db,days):
    if days:
        today = datetime.today()
        last_day = today - timedelta(days=days)

    data=[]
    for group in groups:
            
            result = {}
            
            
            
            all_user_pipeline =  get_all_users_and_interaction_count(group.get("agent_id"))
            interaction_user_count =await db["interactions"].aggregate(all_user_pipeline).to_list(None)
            records=await get_view_data(db,group.get("user_type"))
            all_users_count, unique_users_counts, total_interactions =await count_all_users_interactions(records,last_day)
            all_interaction_ids,all_user_ids =get_ids_of_interaction_and_user(records,last_day)
            no_of_unique_users = len(set(all_user_ids))
            

            
            result.update({"number_of_users": len(all_user_ids)})
            result.update({"users_percentage": (no_of_unique_users / interaction_user_count[0].get("total_unique_users") * 100)})
            result.update({"number_of_interactions": total_interactions})
            result.update({"interaction_percentages": (total_interactions / interaction_user_count[0].get("total_interaction_count") * 100)})
            

            retention = ((len(all_user_ids) - no_of_unique_users) / no_of_unique_users) * 100
            result.update({"associated_interaction_ids": all_interaction_ids})
            result.update({"retention": retention})
            # print("result :", result)
            # result.update({group.get("user_type"):result})
            # result.update({group.get("user_type"):result})
            data.append({group.get("user_type"):result})
            # result={}
            
            
    return data

def get_required_data(records):
    data=[]
    # print(records)
    for record in records:
        data.append({"total_interactions":record.get("total_interactions"),"_id":record.get("_id")})
        # data.append({"total_interactions":record.get("total_interactions")})
    return data
            

    # return [{k: v for k, v in d.items() if k != 'all_users_count'} for d in records]

      
            
async def get_trend_data(groups,db,request:UserGroupTable):
    if request.days:
        last_day=get_days_difference(request.days)
    if request.iscustom:
        start_date= request.start_date
        end_date=request.end_date

        last_day=request.end_date-request.start_date
    

    
    all_data=[]


    for group in groups:
            
        result = {}
        
        
        
        all_user_pipeline =  get_all_users_and_interaction_count(group.get("agent_id"))
        interaction_user_count =await db["interactions"].aggregate(all_user_pipeline).to_list(None)
        records=await get_view_data(db,group.get("user_type"))
        #  print(records["overall_interactions"])
        data= get_required_data(records[0]["data"])

        print(data)
        all_data.append({group.get("user_type"):data})


    # with open("test_record", 'w') as f:
    #     json.dump(records, f, indent=4)
    print("records: ",all_data)
    return all_data

     

     