import MySQLdb



import config.db_cfg as dbCfg
import tool.db.db_tool as dbToolMd


# mysql字符串类型
mysql_str_type = ["CHAR", "VARCHAR", "TINYBLOB", "TINYTEXT", "BLOB", "TEXT"
                  , "MEDIUMBLOB", "MEDIUMTEXT", "LONGBLOB", "LONGTEXT"
                ]
# 添加小写
mysql_str_type_1 = []
for tmp_type in mysql_str_type:
    mysql_str_type_1.append(tmp_type.lower())
mysql_str_type += mysql_str_type_1

# 数据库管理类
class DbMgr():
    db = None
    cursor = None
    table_map = {}

    # 初始化
    def __init__(self, db_name):
        db_cfg = dbCfg.db_map[db_name]
        db = MySQLdb.Connect(
            host = db_cfg["host"], 
            user = db_cfg["user_name"], 
            password = db_cfg["user_pass"], 
            # db = tmp_db_name, 
            charset='utf8' )
        self.db = db
        self.cursor = db.cursor()
        cursor = self.cursor
        cursor.execute("use %s"%(db_cfg["db_name"]))
        
        # 解析数据库结构
        self.table_map = dbToolMd.analysis_sql_file(db_cfg["sql_path"])
        # 预置sql语句
        self.init_sql_str()

    # 执行sql语句
    def execute(self, sql):
        return self.cursor.execute(sql)

    # 预置sql语句
    def init_sql_str(self):
        # table_obj.key_num = 字段数
        # table_obj.key_list = 字段列表
        # table_obj.select_sql 查找语句
        # table_obj.update_sql 更新语句
        # table_obj.delete_sql 删除语句
        for table_name in self.table_map:
            table_obj = self.table_map[table_name]
            # key值
            key_list = []
            for key_name in table_obj.key_map:
                key_list.append(key_name)
            key_str = ",".join(key_list)
            # 索引
            idx_list = []
            str_idx = 0
            for primary_key in table_obj.primary_key:
                tmp_str = "{0}={{{1}}}"
                # 字段是字符串类型
                if self.is_str_key(table_name, primary_key):
                    tmp_str = "{0}='{{{1}}}'"
                idx_list.append(tmp_str.format(primary_key, str_idx))
                str_idx += 1
            index_str = " and ".join(idx_list)
            
            # 查找语句
            select_sql_str = "SELECT {0} FROM {1} WHERE {2}".format(
                key_str
                , table_name
                , index_str
            )
            table_obj.select_sql = select_sql_str
            table_obj.key_list = key_list
            table_obj.key_num = len(key_list)
            
            # 保存语句
            str_idx = 0
            value_str = ""
            for tmp_key in key_list:
                # 字段是字符串类型
                tmp_str = "{{{0}}},"
                if self.is_str_key(table_name, tmp_key):
                    tmp_str = "'{{{0}}}',"
                value_str += tmp_str.format(str_idx)
                str_idx += 1
            update_sql_str = "REPLACE INTO {0}({1}) VALUES ({2})".format(
                table_name
                , key_str
                , value_str[:-1]
            )
            table_obj.update_sql = update_sql_str
            
            # 删除语句
            table_obj.delete_sql = "DELETE FROM {0} WHERE {1}".format(
                table_name
                , index_str
            )
            
    ## 检查函数
    # 是否是字符串字段
    def is_str_key(self, table_name, key):
        table_obj = self.table_map[table_name]
        key_obj = table_obj.key_map[key]
        if key_obj.type in mysql_str_type:
            return True
        return False
    
    
    
    ## 执行函数
    # 获取数据
    def select(self, table_name, key):
        # 兼容单个key
        if type(key) != type([]):
            key = [key]
        # 获取key列表
        table_obj = self.table_map[table_name]
        select_sql = table_obj.select_sql
        do_sql = select_sql.format(*key)
        ret = self.cursor.execute(do_sql)
        if ret == 1:
            one_results = self.cursor.fetchone()
            info = {}
            # 数据按key_list顺序填入
            for idx in range(table_obj.key_num):
                key_name = table_obj.key_list[idx]
                info[key_name] = one_results[idx]
            return info
        return False

    # 更新数据
    def update(self, table_name, info):
        table_obj = self.table_map[table_name]
        update_sql = table_obj.update_sql
        # 数据按key_list顺序填入
        val_list = []
        for idx in range(table_obj.key_num):
            key_name = table_obj.key_list[idx]
            val_list.append(info[key_name])
        # 执行
        if self.cursor.execute(update_sql.format(*val_list)) == 1:
            self.db.commit()
            return True
        return False
    
    # 删除数据
    def delete(self, table_name, info):
        table_obj = self.table_map[table_name]
        delete_sql = table_obj.delete_sql
        # primary_key按顺序填入
        primary_key_list = []
        for primary_key in table_obj.primary_key:
            primary_key_list.append(info[primary_key])
        # 执行
        if self.cursor.execute(delete_sql.format(*primary_key_list)) == 1:
            self.db.commit()
            return True
        return False

## db测试
# import tool.db.main as dbMainMd
# svr_name = "web_svr"
# dbMainMd.run(svr_name)
# a = DbMgr(svr_name)
# a.select("test", 1)
# info = {
#         "id":1
#         , "val":1
#         , "name":"hw"
#     }
# a.update("test", info)
# new_info = a.select("test", 1)
# print(new_info)
# a.delete("test", new_info)

