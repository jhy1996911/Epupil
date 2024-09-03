import gradio as gr
import coze
import os
os.environ['CURL_CA_BUNDLE'] = ''


def chat(user_in_text: str, prj_chatbot: list, request: gr.Request):
    # 获取 URL 参数
    params = request.query_params
    param_value = params.get("token")

    # 将参数信息添加到对话中
    system_message = f"鉴权信息是: {param_value}\n"
    # prj_chatbot.append((None, system_message))
    yield prj_chatbot


    coze_response = coze.chat(system_message + user_in_text, prj_chatbot)

    prj_chatbot.append([user_in_text, ''])
    yield prj_chatbot

    for chunk_content in coze_response:
        prj_chatbot[-1][1] = f'{prj_chatbot[-1][1]}{chunk_content}'
        yield prj_chatbot


web_title = 'Best Assistant'
title_html = f'<h3 align="center">{web_title}</h3>'

footor = "技术驱动业务，创新引领未来&nbsp;&nbsp;&nbsp;--产研测三剑客"
footer_html = f'<div align="center" style="margin-top: 20px; color: grey;">{footor}</div>'


with gr.Blocks(theme=gr.themes.Soft(), analytics_enabled=False) as demo:
    gr.HTML(title_html)
    with gr.Row():
        with gr.Column():
            chatbot = gr.Chatbot()  # 移除 style 方法调用

            with gr.Row():
                with gr.Column(scale=4):
                    input_text = gr.Textbox(show_label=False, placeholder="请输入你的问题")
                with gr.Column(scale=1, min_width=100):
                    submit_btn = gr.Button("提交", variant="primary")
                with gr.Column(scale=1, min_width=100):
                    clean_btn = gr.Button("清空", variant="stop")

    input_text.submit(chat, [input_text, chatbot], chatbot, api_name="chat")
    input_text.submit(lambda x: '', input_text, input_text)

    submit_btn.click(chat, [input_text, chatbot], chatbot, api_name="chat")
    submit_btn.click(lambda x: '', input_text, input_text)

    clean_btn.click(lambda: [], chatbot, chatbot)
    gr.HTML(footer_html)


demo.title = web_title
# demo.launch(share=True, server_name='123.60.85.50')
demo.launch(share=False, server_name='0.0.0.0')
