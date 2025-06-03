from enum import Enum

# 意图识别支持的意图
class IntentType(str, Enum):
    Chat = "Chat",  # 闲聊(所有以下没有提到的都是闲聊)
    Query = "Query",  # 信息查询
    Report = "Report",  # 获取报告
    Appointment = "Appointment", # 获取预约记录
    Interview = "Interview",  # 查询咨询记录
    
intent_enum_values = [item.name for item in IntentType]