import pymysql
from dbutils.pooled_db import PooledDB

class Database:
    def __init__(self, host, user, password, db, port=3306, mincached=1, maxcached=20):
        # 初始化连接池
        self.pool = PooledDB(
            creator=pymysql,
            maxcached=maxcached,   # 连接池中允许的最大连接数
            mincached=mincached,   # 连接池中保持的最小空闲连接数
            host=host,
            user=user,
            password=password,
            database=db,
            port=port,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )

    def get_connection(self):
        # 从连接池中获取一个连接
        return self.pool.connection()

    def execute(self, sql, params=None):
        # 执行SQL语句
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(sql, params)
            conn.commit()
            return cursor
        except Exception as e:
            print(f"执行SQL时发生错误: {e}")
            conn.rollback()
        finally:
            cursor.close()
            conn.close()

    def fetch_all(self, sql, params=None):
        # 查询多条记录
        cursor = self.execute(sql, params)
        return cursor.fetchall()

    def fetch_one(self, sql, params=None):
        # 查询单条记录
        cursor = self.execute(sql, params)
        return cursor.fetchone()

    def insert(self, table, data):
        # 插入记录
        keys = ', '.join(data.keys())
        values = ', '.join(['%s'] * len(data))
        sql = f"INSERT INTO {table} ({keys}) VALUES ({values})"
        cursor = self.execute(sql, tuple(data.values()))
        print(f"插入成功，ID: {cursor.lastrowid}")
        return cursor.lastrowid

    def update(self, table, data, condition):
        # 更新记录
        set_clause = ', '.join([f"{key}=%s" for key in data.keys()])
        condition_clause = ' AND '.join([f"{key}=%s" for key in condition.keys()])
        sql = f"UPDATE {table} SET {set_clause} WHERE {condition_clause}"
        cursor = self.execute(sql, tuple(data.values()) + tuple(condition.values()))
        print(f"更新成功，影响行数: {cursor.rowcount}")
        return cursor.rowcount

    def delete(self, table, condition):
        # 删除记录
        condition_clause = ' AND '.join([f"{key}=%s" for key in condition.keys()])
        sql = f"DELETE FROM {table} WHERE {condition_clause}"
        cursor = self.execute(sql, tuple(condition.values()))
        print(f"删除成功，影响行数: {cursor.rowcount}")
        return cursor.rowcount

# 使用示例
if __name__ == '__main__':
    db = Database(host='123.60.85.50', port=3356, user='root', password='Asdqwe123!', db='esopAI')

    # 插入数据
    data = {'name': '李四', 'age': 30, 'city': '北京'}
    db.insert('users', data)

    # 查询数据
    result = db.fetch_all("SELECT * FROM users")
    print(result)

    # 更新数据
    update_data = {'age': 31}
    condition = {'name': '李四'}
    db.update('users', update_data, condition)

    # 删除数据
    delete_condition = {'name': '李四'}
    db.delete('users', delete_condition)
