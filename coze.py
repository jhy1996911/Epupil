# -- coding: utf-8 --**
import json

import requests

url = 'https://api.coze.cn/v3/chat'
headers = {
    "Authorization": "Bearer pat_yi6XzJLzdPpCCpQ5Cp18rB72xVvkwnILyKqnFGJ3DxPUnK3nMAYNJgxPFprxLQCp",
    "Content-Type": "application/json",
    # "Accept": "*/*",
    # "Host": "api.coze.com",
    # "Connection": "keep-alive"
}

data = {
    # "conversation_id": "123",
    "bot_id": "7408901898235281427",
    "user_id": "111",
    "stream": True,
    "auto_save_history": True
}


def chat(query, history):
    # chat_history = []
    # for hist_item in history:
    #     chat_history.append({'role': 'user', 'type': 'query', 'content': hist_item[0], "content_type": "text"})
    #     chat_history.append({'role': 'assistant', 'type': 'answer', 'content': hist_item[1], "content_type": "text"})

    print("用户说:", query)
    data['additional_messages'] = [{"role": "user", "content": query, "content_type": "text"}]
    # data['additional_messages']=data['additional_messages'].encode('utf-8')
    # data['chat_history'] = chat_history

    data_json = json.dumps(data)
    # data_json_code = data_json.encode('utf-8')
    # headers_json = json.dumps(headers)
    # headers_json = headers_json.encode('utf-8')
    # print(data_json)
    # print(headers)
    response = requests.post(url, headers=headers, data=data_json)

    for line in response.iter_lines():
        # print(line)
        if line:
            decoded_line = line.decode('utf-8')
            print(decoded_line)
            event = extract_event_type(decoded_line)
            if event is not None and event == "[DONE]":
                break

            if event is None:
                json_data = json.loads(decoded_line.split("data:")[-1])
                if 'type' in json_data and json_data['type'] == 'answer':
                    yield json_data['content']


def extract_event_type(event_str):
    # 判断字符串是否以"event:"开头
    if event_str.startswith("event:"):
        # 使用split()方法以":"分割字符串，并取分割后的第二个元素
        event_type = event_str.split(":", 1)[1]
        return event_type
    else:
        return None  # 如果不以"event:"开头，则返回None或你想要的任何默认值
