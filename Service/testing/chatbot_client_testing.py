import httpx
import asyncio
from pydantic import BaseModel

# Define a Pydantic model to validate and serialize input data for chatbot requests
class ChatbotRequest(BaseModel):
    # The context or background information to assist the chatbot in understanding the query
    context: str
    
    # A prompt or instruction that guides the chatbot's response
    prompt: str

    # The user's query to be processed by the chatbot
    query: str
    

# 定义输出数据结构 (ChatbotResponse)
class ChatbotResponse(BaseModel):
    response: str


def get_context():
    # 打开文件并读取内容
    with open(r'C:\Users\Administrator\Desktop\LLM\context.txt', 'r', encoding='utf-8') as file:
        content = file.read()
        return content

# 构造请求数据
def create_chatbot_request():
    # 示例心理咨询对话
    # query = "请基于对话内容提取来访者主观描述。来访者主观描述指来访者对自己当前情绪、认知、行为或问题的主观感受。请关注他们如何描述自己的内心世界、情绪状态、对问题的看法等。"
#     query = '''请基于对话内容提取来访者客观描述，包括但不限于：
# 1）咨询师观察：来访者的外貌、表情、肢体语言、语言风格等。
# 2）测试结果：相关心理测试（如焦虑、抑郁量表等）的具体得分或结果。
# 3）医院就诊结果：如体检报告、医生诊断、检查结果等。 '''
    # context = "学生：老师，我最近感觉特别焦虑，每天都很紧张，心情一直很低落，尤其是考试快到了，我总是担心自己做不好。心理咨询师：我理解你的感受，考试的压力确实会让人感觉焦虑。你能具体说说，是什么让你特别担心自己做不好呢？ 学生：我觉得自己做题速度很慢，考试的时候总是想着自己可能会答错，觉得压力特别大。心理咨询师：这种担心其实是很常见的，特别是在高压的环境下。你是否有过类似的情境，结果并没有像你想象的那么糟糕？学生：嗯，有时候我考试前也很担心，但最终成绩还好。不过我总是担心自己会在某次考试中失败。心理咨询师：你的焦虑其实是一种对未来的担忧，尝试去接受这些不确定性，给自己一些正面的肯定。你有没有尝试过深呼吸或冥想来放松自己？学生：我还没试过，但听起来不错，我会试试的。"
    
    query = '''请基于对话内容提取出与"心理评估"和
"个案概念化"相关的部分。
1) 心理评估：是通过对来访者的行为、情绪、思维等方面进行评估，收集数据来判断其心理健康状况的过程。通常包括面谈、问卷、标准化测试等。
2) 个案概念化：是在评估的基础上，心理咨询师对来访者的心理问题进行分析和整合，帮助制定治疗计划。它通常包括对问题根源的理解、心理机制的探索等。
请从对话中提取出与这些概念相关的内容'''
    context = get_context()
    # print(context)
    prompt = "当前上下文描述了一个情境：\n<Context>\n{context}\n<Context>\n这是一个通用的聊天对话。如果该对话是跟心理咨询无关, 请直接回答:聊天内容与问题无关, 否则请以第一人称的口吻直接回答以下问题。请确保回答直接、准确地针对问题本身，不要添加额外的背景信息或建议。如果问题与上下文无关，请直接说明我们没有讨论过这个话题，并提供一个简洁的通用回答，而不是额外的信息。\n问题：{input}\n"
    
    return ChatbotRequest(query=query, context=context, prompt=prompt)

def send_chatbot_request():
    chatbot_request = create_chatbot_request()
    url = "http://0.0.0.0:8000/chatbot"
    headers = {"Content-Type": "application/json"}  # 确保 Content-Type 正确

    # 自定义 timeout 配置
    timeout = httpx.Timeout(None)  # None 表示禁用超时限制

    with httpx.Client(timeout=timeout) as client:
        response = client.post(url, json=chatbot_request.dict(), headers=headers)

        print("Response status code:", response.status_code)
        print("Response content:", response.text)

        if response.status_code == 200:
            try:
                chatbot_response = ChatbotResponse(**response.json())
                print("Chatbot Response:", chatbot_response.response)
            except Exception as e:
                print("Error parsing response JSON:", e)
        else:
            print(f"Request failed with status code {response.status_code}")


send_chatbot_request()