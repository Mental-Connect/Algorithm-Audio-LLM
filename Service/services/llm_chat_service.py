import json
from Service.model.entity import Entity
from Service.common.http.llm_chat_request import LLMChatRequest
from Service.model.chatbot import chatbot
from Service.model.entity import EntityEnum, entity_enum_values
from Service.model.intent_enum import IntentEnum, intent_enum_values
from Service.database.database_manager import databae_manager
from Service.common.user_finder import user_finder

# 和大语言模型聊天
# request 学校, 用户, 消息, 上下文
async def llm_chat(request: LLMChatRequest) -> str:
    # 意图识别
    intent_type = await __get_intent(request=request)
    
    # 对不同意图做不同处理
    match intent_type:
        # 当意图为查询预约咨询信息时
        case IntentEnum.Appointment:
            return __get_appointment(request=request)
        case IntentEnum.Chat:
            return __chit_chat(request=request)
        case IntentEnum.Query:
            return __get_user_info(request=request)
        case IntentEnum.Report:
            return __generate_report(request=request)
        case IntentEnum.Interview:
            return __get_interview(request=request)
    return ""

# 生成个人报告
async def __generate_report(request:LLMChatRequest):
    # 实体识别
    entity = await __get_entity(query=request.query)
    users = await __get_users(name=entity.user_name, school_id=request.school_id)
    result = ""
    for user in users:
        # todo ai 整理心理健康问题
        # todo 搜索知识
        result = f"{result}\n\t"
    
    return result

# 获取用户基本信息
async def __get_user_info(request: LLMChatRequest):
    # 实体识别
    entity = await __get_entity(query=request.query)
    users = await __get_users(name=entity.user_name, school_id=request.school_id)
    result = ""
    for user in users:
        # todo ai整理用户信息
        # user_info = 
        result = f"{result}\n\t"
    return result
    
# 闲聊
def __chit_chat(request: LLMChatRequest) -> str:
    prompt = "{input}"
    result = chatbot(context=request.context, prompt=prompt, query=request.query)
    return result

# 查询预约信息
async def __get_appointment(request: LLMChatRequest) -> str:
    # 实体识别
    entity = await __get_entity(query=request.query)
    users = await __get_users(entity.user_name)
    
    result = ""
    # 返回所有人的最新预约信息
    for user in users:
        interview = databae_manager.get_student_appointment(user_id=user["_id"])
        if interview is not None:
            # todo 让ai整理预约信息
            result = f"{result}\n\t"
    return result

# 查询访谈信息
async def __get_interview(request: LLMChatRequest):
    # 实体识别
    entity = await __get_entity(query=request.query)
    users = await __get_users(entity.user_name)
    
    result = ""
    # 返回所有人的最新预约信息
    for user in users:
        interview = databae_manager.get_student_appointment(user_id=user["_id"])
        if interview is not None:
            # todo 让ai整理预约信息
            result = f"{result}\n\t"
    return result

# 根据姓名查询用户
# 查询不到就查询相似姓名的用户
async def __get_users(name:str, school_id:str):
    # 数据库查询该用户
    users = []
    users.append(databae_manager.get_school_user(name=name, school_id=school_id))
    # 数据库中没有该用户时查询相似姓名的用户
    if len(users) == 0:
        user_names = user_finder.get_match_names(name)
        for user_name in user_names:
            users.append(databae_manager.get_school_user(user_name, school_id))
            
# 判断意图
async def __get_intent(request: LLMChatRequest) -> IntentEnum:
    # 意图识别提示词
    intent_prompt = f"请判断用户的意图, 仅从以下类别中选择一个: f{', '.join(intent_enum_values)}.不要解释,也不要输入除枚举值以外的任何东西.\n:用户文本:{input}"
    response_text = chatbot(context=request.context, prompt = intent_prompt, query=request.query)
    print(response_text)
    return IntentEnum(response_text)

# 获取实体
async def __get_entity(query: str) -> Entity:
    # 实体提取提示词
    entity_prompt = f"你是一个信息抽取助手,任务是从用于输入的文本中提取有用的实体信息. 请从输入文本中提取出实体,并用json格式输出,字段包括: f{', '.join(entity_enum_values)}.不要解释,也不要输入除json以外的任何东西, 如果没有某些字段,值设为null.\n输入的文本:{input}"
    response_text = chatbot(context="", prompt = entity_prompt, query=query)
    response_json = json.loads(response_text)
    e = Entity()
    e.user_name = response_json.get(EntityEnum.person.name)
    print(e.user_name)
    return e