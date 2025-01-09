import httpx
import asyncio
import time
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
  
    query = '''请基于对话内容提取出与"心理评估"和"个案概念化"相关的部分。
            1) 心理评估：是通过对来访者的行为、情绪、思维等方面进行评估，收集数据来判断其心理健康状况的过程。通常包括面谈、问卷、标准化测试等。
            2) 个案概念化：是在评估的基础上，心理咨询师对来访者的心理问题进行分析和整合，帮助制定治疗计划。它通常包括对问题根源的理解、心理机制的探索等。
            请从对话中提取出与这些概念相关的内容'''
    
    context = get_context()
    prompt = "当前上下文描述了一个情境：\n<Context>\n{context}\n<Context>\n这是一个通用的聊天对话。如果该对话是跟心理咨询无关, 请直接回答:聊天内容与问题无关, 否则请以第一人称的口吻直接回答以下问题。请确保回答直接、准确地针对问题本身，不要添加额外的背景信息或建议。如果问题与上下文无关，请直接说明我们没有讨论过这个话题，并提供一个简洁的通用回答，而不是额外的信息。\n问题：{input}\n"
    return ChatbotRequest(query=query, context=context, prompt=prompt)

def send_chatbot_request():
    chatbot_request = create_chatbot_request()
    # url = "http://0.0.0.0:8000/chatbot"
    url = "http://121.41.3.58:8000/chatbot"
    headers = {"Content-Type": "application/json"}  # 确保 Content-Type 正确

    # 自定义 timeout 配置
    timeout = httpx.Timeout(None)  # None 表示禁用超时限制

    with httpx.Client(timeout=timeout) as client:
        t1 = time.time()
        response = client.post(url, json=chatbot_request.dict(), headers=headers)
        t2 = time.time()
        print(f"函数执行时间：{t2-t1}秒")

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