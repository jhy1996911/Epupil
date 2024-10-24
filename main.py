import gradio as gr

import ChatTimer
import coze
import os
import random
import string
import asyncio
import time
import threading

from Database import Database
from feishu import add_record, get_access_token

os.environ['CURL_CA_BUNDLE'] = ''

db = Database(host='123.60.85.50', port=3356, user='root', password='Asdqwe123!', db='esopAI')

USER_ID = "user_id"


# 生成唯一的会话 ID
def generate_conversation_id():
    return ''.join(random.choices(string.digits, k=16))


# 定义一个全局变量存储用户的会话ID、定时器和最后活动时间
user_conversation = {}


# 用户聊天处理逻辑
def chat(user_in_text: str, prj_chatbot: list, user_id_status: dict):
    if user_id_status[USER_ID] is None:
        user_id_status[USER_ID] = generate_conversation_id()
    # 检查前端是否传递了有效的用户会话ID
    print("user_id=", user_id_status[USER_ID])
    # 向用户展示消息
    yield prj_chatbot

    # 取消之前的定时器，重置为2分钟
    if user_id_status[USER_ID] in user_conversation:
        timer = user_conversation[user_id_status[USER_ID]]
        # 检查是否为 threading.Timer 实例
        if isinstance(timer, threading.Timer):
            timer.cancel()

    user_conversation[user_id_status[USER_ID]] = threading.Timer(60, reset_conversation_id,
                                                                 [user_id_status, prj_chatbot])
    user_conversation[user_id_status[USER_ID]].start()

    coze_response = coze.chat(user_in_text, prj_chatbot, user_id_status[USER_ID])

    prj_chatbot.append([user_in_text, ''])
    yield prj_chatbot

    for chunk_content in coze_response:
        prj_chatbot[-1][1] = f'{prj_chatbot[-1][1]}{chunk_content}'
        yield prj_chatbot

    data = {}
    data['role'] = "user"
    data['content'] = user_in_text
    data['user_id'] = user_id_status[USER_ID]
    db.insert('user_chat_log', data)

    data['role'] = "ai"
    data['content'] = prj_chatbot[-1][1]
    db.insert('user_chat_log', data)
    addUserFeishuLog(prj_chatbot, user_id_status, user_in_text)
    addAiFeishuLog(prj_chatbot, user_id_status)


def addAiFeishuLog(prj_chatbot, user_id_status):
    new_record = {}
    new_record['对话标识'] = user_id_status[USER_ID]
    new_record['角色'] = "ai"
    new_record['内容'] = prj_chatbot[-1][1]
    access_token = get_access_token()
    add_record(access_token, new_record)


def addUserFeishuLog(prj_chatbot, user_id_status, user_in_text):
    new_record = {}
    new_record['对话标识'] = user_id_status[USER_ID]
    new_record['角色'] = "user"
    new_record['内容'] = user_in_text
    access_token = get_access_token()
    add_record(access_token, new_record)


# 重置用户的会话ID，并给用户提示
def reset_conversation_id(user_id_status: dict, prj_chatbot):
    data = {}
    data['status'] = 'finish'
    condition = {}
    condition['user_id'] = user_id_status[USER_ID]
    db.update('user_chat_log', data, condition)

    gr.State().change()

    new_id = generate_conversation_id()  # 生成新的会话ID
    print(f"用户 {user_id_status[USER_ID]} 会话超时，生成新会话ID: {new_id}")
    user_conversation[new_id] = {"timer": None, "last_active": time.time()}  # 初始化新的会话ID
    user_id_status[USER_ID] = new_id

    ChatTimer.process_summary_data(db)
    # 添加提示文案到 prj_chatbot
    # prj_chatbot.append(["系统提示", "您已经两分钟未回复，已生成新的会话ID，请继续提问。"])


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


    ChatTimer.process_summary_data(db)

    user_id_status = gr.State({USER_ID: None})

    # 修改此处，在前端传递用户ID
    input_text.submit(chat, [input_text, chatbot, user_id_status], chatbot, api_name="chat")

    input_text.submit(lambda x: '', input_text, input_text)

    submit_btn.click(chat, [input_text, chatbot, user_id_status], chatbot, api_name="chat")

    submit_btn.click(lambda x: '', input_text, input_text)

    clean_btn.click(reset_conversation, chatbot, chatbot)
    gr.HTML(footer_html)

demo.title = web_title
demo.queue(default_concurrency_limit=10).launch(share=False, server_name='0.0.0.0')
