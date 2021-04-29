from bottle import default_app, run, get, post, request
from beaker.middleware import SessionMiddleware
import sys
import json
import gevent
from gevent import monkey
monkey.patch_all()
import requests # 必须在 monkey后

import config.net as netCfg
import load_balance_svr.load_balance_svr as loadBalanceSvrMd

load_balance_svr_ins = loadBalanceSvrMd.get_ins()

# 协议
# 添加新的服务器
@post('/add_ser')
def add_ser():
    data = request.json
    load_balance_svr_ins.protocol_add_web_svr(data)
    return 

# 设置服务器待处理消息数
@post('/set_msg_num')
def set_msg_num():
    data = request.json
    load_balance_svr_ins.protocol_set_msg_num(data)
    return 

# 获取空闲服务器
@get('/get_min_svr')
def get_min_svr():
    return load_balance_svr_ins.protocol_get_min_svr()


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
    cfg = netCfg.load_balance_cfg
    

    # 运行服务器
    # app_argv = SessionMiddleware(default_app(), session_opts)
    # run(app=app_argv, host=cfg["host"], port=cfg["port"], debug=True, reloader=True, server='gevent')
    run(host=cfg["host"], port=cfg["port"], debug=True, reloader=True, server='paste')
    
    
    
# py load_balance_main.py 
# py load_balance_main.py 
svr_run()








