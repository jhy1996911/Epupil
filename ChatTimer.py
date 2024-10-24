# from Database import Database
import json

import coze
from feishu import get_access_token, add_record
import re


def process_summary_data(db):
    print("开始汇总数据...")
    result = db.fetch_all("select distinct user_id from user_chat_log where status='finish'")
    user_ids = [item['user_id'] for item in result]
    for user_id in user_ids:
        result = db.fetch_all(
            "select content from user_chat_log where role='user' and user_id=" + user_id + " order by id asc")
            # "select content from user_chat_log where user_id=" + user_id + " order by id asc")
        user_contents = [item['content'] for item in result]
        content = "从" + str(user_contents) + (
            "中总结用户的对话，返回信息格式为json格式，如 {\"姓名\":,\"联系方式\":,\"所在公司\":,\"用户诉求\":}")
        print(content)
        history = [content]
        coze_response = coze.chat(content, history, user_id)
        content_response = ""
        for chunk_content in coze_response:
            content_response = content_response + chunk_content
        # print(content_response)


        # pattern = r"姓名:(\S+) 联系方式:(\d+) 所在公司:(\S+) 用户诉求:(.+)"
        # match = re.search(pattern, content_response)

        text = content_response
        # 将匹配到的结果存储为字典

        print("test=", text)
        # result = {
        #     "姓名": re.search(r"姓名:\s*(\S+)", text).group(1),
        #     "联系方式": re.search(r"联系方式:\s*(\d+)", text).group(1),
        #     # "邮箱": re.search(r"邮箱:\s*(\S+)", text).group(1),
        #     "所在公司": re.search(r"所在公司:\s*(\S+)", text).group(1),
        #     "用户诉求": re.search(r"用户诉求:\s*(\S+)", text).group(1)
        # }
        result = json.loads(content_response)
        # result = {
        #     "姓名": re.search(r"姓名:\s*(\S*),", text).group(1) if re.search(r"姓名:\s*(\S*),", text) else "",
        #     "联系方式": re.search(r"联系方式:\s*(\d*),", text).group(1) if re.search(r"联系方式:\s*(\d*),", text) else "",
        #     # "邮箱": re.search(r"邮箱:\s*(\S*)", text).group(1) if re.search(r"邮箱:\s*(\S*)", text) else "",
        #     "所在公司": re.search(r"所在公司:\s*(\S*),", text).group(1) if re.search(r"所在公司:\s*(\S*),", text) else "",
        #     "用户诉求": re.search(r"用户诉求:\s*(\S*)", text).group(1) if re.search(r"用户诉求:\s*(\S*)", text) else ""
        # }

        print("result=", result)
        if result is not None and result["联系方式"] is not None:
            access_token = get_access_token()
            # 新增记录示例
            result["对话标识"] = user_id
            result["总结"] = text
            added_record = add_record(access_token, result, "tblVp9oQyqVj6Cjq")
            print("新增成功:", added_record)

        data = {}
        data['status'] = 'Summarized'
        condition = {}
        condition['user_id'] = user_id
        db.update('user_chat_log', data, condition)


print("汇总数据完成，结果已保存。")

# if __name__ == '__main__':
#     db = Database(host='123.60.85.50', port=3356, user='root', password='Asdqwe123!', db='esopAI')
#     process_summary_data(db)
