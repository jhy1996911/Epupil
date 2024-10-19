import gradio as gr
import coze
import os
import random
import string
import asyncio
import time
import threading

from Database import Database

os.environ['CURL_CA_BUNDLE'] = ''

db = Database(host='123.60.85.50', port=3356, user='root', password='Asdqwe123!', db='esopAI')


# 生成唯一的会话 ID
def generate_conversation_id():
    return ''.join(random.choices(string.digits, k=16))


# 定义一个全局变量存储用户的会话ID、定时器和最后活动时间
user_conversation = {}


# 用户聊天处理逻辑
async def chat(user_in_text: str, prj_chatbot: list, user_id: str):
    userid1 = gr.State()
    # 检查前端是否传递了有效的用户会话ID
    print("user_id=", user_id)
    print("user_id1=", str(userid1))
    if user_id is None:
        user_id = generate_conversation_id()
    user_conversation[user_id] = {"timer": None, "last_active": time.time()}  # 初始化定时器和活动时间

    # 更新最后活动时间
    # user_conversation[user_id]["last_active"] = time.time()

    # 启动定时器检测
    if user_conversation[user_id]["timer"] is None:
        new_id = await asyncio.create_task(check_timeout(user_id, prj_chatbot))
        if new_id:
            print("user_id=", new_id)
            user_id = new_id  # 更新新的会话ID
            # yield prj_chatbot
    # 向用户展示消息
    yield prj_chatbot
    print("user_id3=", user_id)

    coze_response = coze.chat(user_in_text, prj_chatbot, user_id)

    data = {}
    data['role'] = "user"
    data['content'] = user_in_text
    data['user_id'] = user_id
    db.insert('user_chat_log', data)

    prj_chatbot.append([user_in_text, ''])
    yield prj_chatbot

    for chunk_content in coze_response:
        prj_chatbot[-1][1] = f'{prj_chatbot[-1][1]}{chunk_content}'
        yield prj_chatbot

    data['role'] = "ai"
    data['content'] = prj_chatbot[-1][1]
    db.insert('user_chat_log', data)


# 检查是否超时
async def check_timeout(user_id, prj_chatbot):
    while True:
        await asyncio.sleep(5)  # 每5秒检查一次

        last_active = user_conversation[user_id]["last_active"]
        current_time = time.time()

        if current_time - last_active > 20:  # 如果超过两分钟未活动
            new_id = reset_conversation_id(user_id, prj_chatbot)  # 重置并生成新会话ID
            print("会话超时，生成新会话ID:", new_id)
            return new_id  # 返回新的会话ID，供前端更新

# 重置用户的会话ID，并给用户提示
def reset_conversation_id(user_id, prj_chatbot):
    data = {}
    data['status'] = 'finish'
    condition = {}
    condition['user_id'] = user_id
    db.update('user_chat_log', data, condition)

    new_id = generate_conversation_id()  # 生成新的会话ID
    print(f"用户 {user_id} 会话超时，生成新会话ID: {new_id}")
    user_conversation[new_id] = {"timer": None, "last_active": time.time()}  # 初始化新的会话ID

    # 添加提示文案到 prj_chatbot
    # prj_chatbot.append(["系统提示", "您已经两分钟未回复，已生成新的会话ID，请继续提问。"])

    update_user_id_state(new_id)
    return new_id  # 返回新的会话ID，供前端更新


# 在前端调用reset_conversation_id后，更新状态
def update_user_id_state(new_id):
    return gr.State(value=new_id)  # 更新前端状态为新的ID


web_title = 'Best Assistant'
title_html = f'<h3 align="center">{web_title}</h3>'

footor = "技术驱动业务，创新引领未来&nbsp;&nbsp;&nbsp;--产研测三剑客"
footer_html = f'<div align="center" style="margin-top: 20px; color: grey;">{footor}</div>'

with gr.Blocks(theme=gr.themes.Soft(), analytics_enabled=False) as demo:
    gr.HTML(title_html)
    with gr.Row():
        with gr.Column():
            chatbot = gr.Chatbot()

            with gr.Row():
                with gr.Column(scale=4):
                    input_text = gr.Textbox(show_label=False, placeholder="请输入你的问题")
                with gr.Column(scale=1, min_width=100):
                    submit_btn = gr.Button("提交", variant="primary")
                with gr.Column(scale=1, min_width=100):
                    clean_btn = gr.Button("清空", variant="stop")


    def reset_conversation(param):
        return []


    id = generate_conversation_id()
    update_user_id_state(id)
    user_id = gr.State(value=id)

    # 修改此处，在前端传递用户ID
    input_text.submit(chat, [input_text, chatbot, user_id], chatbot, api_name="chat")

    input_text.submit(lambda x: '', input_text, input_text)

    submit_btn.click(chat, [input_text, chatbot, user_id], chatbot, api_name="chat")

    submit_btn.click(lambda x: '', input_text, input_text)

    clean_btn.click(reset_conversation, chatbot, chatbot)
    gr.HTML(footer_html)

demo.title = web_title
demo.queue(default_concurrency_limit=10).launch(share=False, server_name='0.0.0.0')
