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
    print(response.text)

    for line in response.iter_lines():
        print(line)
        if line:
            decoded_line = line.decode('utf-8')
            json_data = json.loads(decoded_line.split("data:")[-1])

            # if json_data['event'] == 'done':
            #     break
            # else:
            if json_data['type'] == 'answer':
                yield json_data['content']
