from bottle import run, get, request
from gevent import monkey
monkey.patch_all()
import sys


import web_svr.web_svr as WebSvrMd
import lib.db as dbMd
import config.net as netCfg
import config.db_cfg as dbCfg


# 获取配置
svr_id = sys.argv[1]
cfg = netCfg.web_svr_cfg[svr_id]

# 数据单例
dbMgr = dbMd.get_ins(dbCfg.db_map[cfg["db_cfg"]])
# 服务器单例
web_svr_ins = WebSvrMd.get_ins(cfg)



# 协议
# 获取值
@get('/get_val')
def get_val():
    key = web_svr_ins.get_val(request.query)
    return key

# 客户端尝试连接
@get('/check_svr')
def check_svr():
    return "1"





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
    web_svr_ins.connect_load_balance_thread()
    
    # 运行服务器
    # app_argv = SessionMiddleware(default_app(), session_opts)
    # run(app=app_argv, host=cfg["host"], port=cfg["port"], debug=True, reloader=True, server='gevent')
    run(host=cfg["host"], port=cfg["port"], debug=True, reloader=True, server='paste')
    
    
# py web_svr_main.py 服务器配置
# py web_svr_main.py 1
svr_run()








