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
            __get_appointment(request=request)
        # case IntentEnum. ...
        #     ...
        
    # todo 2.实体提取
    # todo 3.数据查询
    # todo 4.知识检索
    # todo 5.构建prompt
    # todo 6.询问llm返回结果
    return ""

# 判断意图
async def __get_intent(request: LLMChatRequest) -> IntentEnum:
    # 意图识别提示词
    intent_prompt = f"请判断用户的意图, 仅从以下类别中选择一个: f{', '.join(intent_enum_values)}.不要解释,也不要输入除枚举值以外的任何东西.\n:用户文本:{input}"
    response_text = chatbot(context=request.context, prompt = intent_prompt, query=request.query)
    print(response_text)
    return IntentEnum(response_text)

# 获取实体
async def __get_entity(request: LLMChatRequest) -> Entity:
    # 实体提取提示词
    entity_prompt = f"你是一个信息抽取助手,任务是从用于输入的文本中提取有用的实体信息. 请从输入文本中提取出实体,并用json格式输出,字段包括: f{', '.join(entity_enum_values)}.不要解释,也不要输入除json以外的任何东西, 如果没有某些字段,值设为null.\n输入的文本:{input}"
    response_text = chatbot(context=request.context, prompt = entity_prompt, query=request.query)
    response_json = json.loads(response_text)
    e = Entity()
    e.user_name = response_json.get(EntityEnum.person.name)
    print(e.user_name)
    return e

# 生成个人报告
def __generate_report():
    pass

# 获取用户基本信息
def __get_user_info():
    pass

# 闲聊
def __chit_chat():
    pass

# 查询预约信息
async def __get_appointment(request: LLMChatRequest) -> str:
    entity = await __get_entity(request=request)
    users = []
    users.append(databae_manager.get_school_user(entity.user_name, request.school_id))
    if len(users) == 0:
        user_names = user_finder.get_match_names(entity.user_name)
        for user_name in user_names:
            users.append(databae_manager.get_school_user(entity.user_name, request.school_id))
    
    result = ""
    for user in users:
        interview = databae_manager.get_student_appointment(user_id=user["_id"])
        if interview is not None:
            # 让ai整理预约信息
            result = f"{result}\n\t"
    return result

# 查询访谈信息
def __get_interview():
    pass

# 姓名处理
def __user_name_process() -> list[str]:
    pass