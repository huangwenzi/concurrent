from bottle import run, get, post, request
from gevent import monkey
monkey.patch_all()
import sys


import cache_svr.cache_svr as cacheSvrMd
import lib.db as dbMd
import config.net as netCfg
import config.db_cfg as dbCfg


# 获取配置
cache_type = sys.argv[1]
svr_id = sys.argv[2]
cfg = netCfg.cache_cfg[cache_type][svr_id]


# 数据单例
dbMgr = dbMd.get_ins(dbCfg.db_map[cfg["db_cfg"]])
# 服务器单例
cache_svr_ins = cacheSvrMd.get_ins(cfg)



# 协议
# web_svr尝试连接
@get('/check_svr')
def check_svr():
    return "1"

# 获取值
@post('/get_val')
def get_val():
    return cache_svr_ins.get_val(request.json)


# r用
# write_cache 同步数据
@post('/sync_val')
def get_val():
    cache_svr_ins.sync_val(request.json)
    return ""


 
# w用
# 添加read_cache 
@post('/add_ser')
def get_val():
    cache_svr_ins.add_ser(request.json)
    return 

# 修改val
@post('/change_val')
def get_val():
    cache_svr_ins.change_val(request.json)
    return 







# 服务器
# 设置session参数
session_opts = {
    'session.type': 'file',
    'session.cookie_expires': 3600,
    'session.data_dir': '/tmp/sessions/simple',
    'session.auto': True
}

# 函数主入口
def svr_run():
    # 通知负载均衡，服务器准备就绪
    cache_svr_ins.connect_load_balance_thread()
    # 通知write_cache，服务器准备就绪
    cache_svr_ins.connect_write_cache_thread()
    
    # 运行服务器
    # app_argv = SessionMiddleware(default_app(), session_opts)
    # run(app=app_argv, host=cfg["host"], port=cfg["port"], debug=True, reloader=True, server='gevent')
    run(host=cfg["host"], port=cfg["port"], debug=True, reloader=True, server='paste')
    
    
# py cache_main.py cache类型 服务器配置 
# py cache_main.py write 1
# py cache_main.py read 101
svr_run()








