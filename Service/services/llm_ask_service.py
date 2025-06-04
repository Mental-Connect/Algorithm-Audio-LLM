import json
from xml.dom.minidom import Entity
from Service.common.http.llm_ask_request import LLMAskRequest
from Service.model.chatbot import chatbot
from Service.model.entity import EntityType, entity_enum_values
from Service.model.intent import IntentType, intent_enum_values

# 和大语言模型聊天
# request 学校, 用户, 消息, 上下文
async def llm_ask(request: LLMAskRequest) -> str:
    try:
        intent_type = await get_intent(request=request)
        e = await get_entity(request=request)
    except:
        raise "Error Uploading the transcription."
    return e

# 意图识别提示词
intent_prompt = f"请判断用户的意图, 仅从以下类别中选择一个: f{', '.join(intent_enum_values)}.不要解释,也不要输入除枚举值以外的任何东西.\n:用户文本:{input}"

# 判断意图
async def get_intent(request: LLMAskRequest) -> IntentType:
    try:
        response_text = chatbot(context=request.context, prompt = intent_prompt, query=request.query)
    except:
        raise "Error Uploading the transcription."
    return IntentType(response_text)

# 实体提取提示词
entity_prompt = f"你是一个信息抽取助手,任务是从用于输入的文本中提取有用的实体信息. 请从输入文本中提取出实体,并用json格式输出,字段包括: f{', '.join(entity_enum_values)}.不要解释,也不要输入除json以外的任何东西, 如果没有某些字段,值设为null.\n输入的文本:{input}"

# 获取实体
async def get_entity(request: LLMAskRequest) -> Entity:
    try:
        response_text = chatbot(context=request.context, prompt = entity_prompt, query=request.query)
        response_json = json.loads(response_text)
        e = Entity()
        e.user_name = response_json.get(EntityType.person.name)
    except:
        raise "Error Uploading the transcription."
    return e

# 生成个人报告
def generate_report():
    pass

# 获取用户基本信息
def get_user_info():
    pass

# 闲聊
def chit_chat():
    pass

# 查询预约信息
def get_appointment():
    pass

# 查询访谈信息
def get_interview():
    pass

# 姓名处理
def user_name_process() -> list[str]:
    pass