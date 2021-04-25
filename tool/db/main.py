import MySQLdb



import tool.db.db_tool as dbToolMd
import config.db_cfg as dbCfg

# 暂时这样写， 后面改成sys.agv的格式
db_cfg = dbCfg.db_map["web_svr"]

def run():
    # 解析sql文件
    table_map = dbToolMd.analysis_sql_file(db_cfg["sql_path"])
    # 导出数据库表结构
    db = MySQLdb.Connect(
        host = db_cfg["host"], 
        user = db_cfg["user_name"], 
        password = db_cfg["user_pass"], 
        # db = tmp_db_name, 
        charset='utf8' )
    cursor = db.cursor()
    db_table_map = dbToolMd.analysis_db_table(cursor, db_cfg["db_name"])
    # 对比差异,生成sql文件
    sql_str = dbToolMd.create_diff_sql(table_map, db_table_map)
    # 导出一份到本地
    with open(db_cfg["out_path"], 'w', encoding = 'utf8') as f:
        f.write(sql_str)
    # 执行修改
    cursor.execute(sql_str)

run()

