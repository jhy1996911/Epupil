import requests
import json

# 飞书 API 配置
APP_ID = 'cli_a4531fd229b9900d'
APP_SECRET = '5PvycuNly4uIKQa5OiQRWdtub6crv2qm'
TENANT_ACCESS_TOKEN_URL = 'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal'
SPREADSHEET_ID = 'OW39buX1Oay4hZsvzhmcMQYTn1g'
TABLE_ID = 'tblXTL9tp5wBuTNg'
FEISHU_API_BASE_URL = 'https://open.feishu.cn/open-apis'


# 获取 tenant_access_token
def get_access_token():
    url = TENANT_ACCESS_TOKEN_URL
    headers = {
        "Content-Type": "application/json; charset=utf-8"
    }
    body = {
        "app_id": APP_ID,
        "app_secret": APP_SECRET
    }
    response = requests.post(url, headers=headers, data=json.dumps(body))
    if response.status_code == 200:
        token = response.json().get("tenant_access_token")
        return token
    else:
        raise Exception("Failed to get access token: " + response.text)


# 新增记录到飞书表格
def add_record(access_token, record_data, table_id=TABLE_ID):
    url = f"{FEISHU_API_BASE_URL}/bitable/v1/apps/{SPREADSHEET_ID}/tables/{table_id}/records"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json; charset=utf-8"
    }
    body = {
        "fields": record_data  # record_data 应该是一个包含表格字段和值的字典
    }

    response = requests.post(url, headers=headers, data=json.dumps(body))

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to add record: {response.text}")


# 更新飞书表格中的记录
def update_record(access_token, record_id, updated_data):
    url = f"{FEISHU_API_BASE_URL}/bitable/v1/apps/{SPREADSHEET_ID}/tables/{TABLE_ID}/records/{record_id}"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json; charset=utf-8"
    }
    body = {
        "fields": updated_data  # updated_data 是要更新的字段和对应的值
    }

    response = requests.put(url, headers=headers, data=json.dumps(body))

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to update record: {response.text}")


if __name__ == "__main__":
    try:
        print("正在获取 Access Token...")
        access_token = get_access_token()
        print("成功获取access_token", access_token)

        # 新增记录示例
        new_record = {
            "对话标识": "1234567",
            "角色": "ai",
            "内容": "研发部"
        }
        print("正在新增记录...")
        added_record = add_record(access_token, new_record)
        print("新增成功:", added_record)

    except Exception as e:
        print(f"操作失败: {e}")
