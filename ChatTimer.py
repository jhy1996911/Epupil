# from Database import Database
import coze


def process_summary_data(db):
    print("开始汇总数据...")
    result = db.fetch_all("select distinct user_id from user_chat_log where status='finish'")
    user_ids = [item['user_id'] for item in result]
    for user_id in user_ids:
        result = db.fetch_all(
            "select content from user_chat_log where role='user' and user_id=" + user_id + " order by id desc")
        user_contents = [item['content'] for item in result]
        content = "从" + str(user_contents) + "中总结用户诉求，返回信息格式为 [用户诉求:]"
        print(content)
        history = [content]
        coze_response = coze.chat(content, history, user_id)
        content_response = ""
        for chunk_content in coze_response:
            content_response = content_response + chunk_content
        print(content_response)
        data = {}
        data['status'] = 'Summarized'
        condition = {}
        condition['user_id'] = user_id
        db.update('user_chat_log', data, condition)
    print("汇总数据完成，结果已保存。")


# if __name__ == '__main__':
#     db = Database(host='123.60.85.50', port=3356, user='root', password='Asdqwe123!', db='esopAI')
#     process_summary_data(db)
