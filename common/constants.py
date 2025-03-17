import os
from pathlib import Path
class StatusCode:
    SUCCESS = 200
    CREATED = 201
    BAD_REQUEST = 400
    NOT_FOUND = 404
    SERVER_ERROR = 500

class Messages:
    SUCCESS = "Successfully fetched"
    CREATED = "Created successfully"
    BAD_REQUEST = "Invalid request"
    NOT_FOUND = "Resource not found"
    SERVER_ERROR = "Internal server error"


CHAT_DATA_STORAGE_PATH="E:\isyenergy\mongodb\sessions_json"
CHAT_FILENAME_INITIAL="Session_"
CHAT_DATA_EXTENSION= ".json"



#################################################################################
#############   User Types ###############################

VIEW_CREATE_CONSTANT_STRING = "user_type_view_"



#==================================================================================
#======================Constants for date filters==================================

HOURLY_INTERVAL= 1
DAILY_INTERVAL = 12
TWO_DAYS_INTERVAL=21
THREE_DAYS_INTERVAL=36
WEEKLY_INTERVAL=84
TEN_DAYS_INTERVAL =120
MONTHLY_INTERVAL =180
TWO_MONTHLY_INTERVAL=365    # after 12 months 
THREE_MONTHLY_INTERVAL=730  # 2*365 , after 24 months 
YERALY_INTERVAL=1095   #  3*365 DAYS


#===========================================================
# ===============  common utils  ===========================

DB_DATE_FIELD="timestamp"

