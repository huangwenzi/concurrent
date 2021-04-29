from bottle import default_app, run, get, post, request
import gevent
from gevent import monkey
monkey.patch_all()
from beaker.middleware import SessionMiddleware
import sys
import requests
import json
import time

import web_svr.web_svr as WebSvrMd
import config.net as netCfg


# 服务器单例
web_svr_ins = WebSvrMd.get_ins()


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
    # 获取配置
    svr_id = sys.argv[1]
    # cfg = netCfg.web_svr_cfg["1"]
    cfg = netCfg.web_svr_cfg[svr_id]
    
    # 通知负载均衡，服务器准备就绪
    web_svr_ins.connect_load_balance_thread()
    
    # 运行服务器
    # app_argv = SessionMiddleware(default_app(), session_opts)
    # run(app=app_argv, host=cfg["host"], port=cfg["port"], debug=True, reloader=True, server='gevent')
    run(host=cfg["host"], port=cfg["port"], debug=True, reloader=True, server='paste')
    
    
# py web_svr_main.py 服务器配置 数据库配置
# py web_svr_main.py 1 web_svr
svr_run()








