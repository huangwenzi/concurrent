import sqlite3

# 数据库表名
_table_name = "test_1"

# 数据库管理类


class DbMgr():
    conn = None
    mydb = None

    # 初始化
    def __init__(self):
        # 将 con 设定为全局连接
        self.conn = sqlite3.connect('test_1.db')
        # 获取连接的 cursor，只有获取了 cursor，我们才能进行各种操作
        self.mydb = self.conn.cursor()
        # 检查表是否存在
        self.mydb.execute("SELECT name FROM sqlite_master WHERE type='table';")
        # 使用 fetchall 函数，将结果集（多维元组）存入 rows 里面
        rows = self.mydb.fetchall()
        tableArr = []
        for tmp_rows in rows:
            for table_name in tmp_rows:
                tableArr.append(table_name)
        if _table_name not in tableArr:
            try:
                self.mydb.execute('''CREATE TABLE %s
                            (ID INT PRIMARY KEY,
                            table_key        CHAR(50),
                            table_val        CHAR(1024));''' % (_table_name))
                self.conn.commit()
            except :
                self.closs()
                self.mydb = None
                self.conn = None
            # self.conn.close()

    # 设置值
    def set_val(self, key, val):
        try:
            # 先检查是否key值存在
            sql_str = 'SELECT * FROM %s WHERE table_key="%s"' % (_table_name, key)
            self.mydb.execute(sql_str)
            rows = self.mydb.fetchall()
            if len(rows) > 0:
                # 存在，直接更新
                sql_str = 'UPDATE %s SET table_val="%s" WHERE table_key="%s"' % (
                    _table_name, val, key)
                self.mydb.execute(sql_str)
            else:
                # 不存在，插入
                sql_str = 'INSERT INTO %s(table_key,table_val) VALUES("%s","%s")' % (
                    _table_name, key, val)
                self.mydb.execute(sql_str)
            self.conn.commit()
        except :
            self.closs()

    # 获取值
    def get_val(self, key):
        sql_str = 'SELECT table_val FROM %s WHERE table_key="%s"' % (
            _table_name, key)
        # sql_str = 'SELECT table_val FROM %s' % (
        #     _table_name)
        self.mydb.execute(sql_str)
        # 使用 fetchall 函数，将结果集（多维元组）存入 rows 里面
        row = self.mydb.fetchone()
        if row:
            return row[0]
        return None

    # 关闭数据库
    def closs(self):
        self.conn.closs()

dbMgr = DbMgr()





