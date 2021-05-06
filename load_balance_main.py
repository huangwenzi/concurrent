from bottle import run, get, post, request
from gevent import monkey
monkey.patch_all()

import config.net as netCfg
import load_balance_svr.load_balance_svr as loadBalanceSvrMd

load_balance_svr_ins = loadBalanceSvrMd.get_ins()

# 协议
# 添加新的服务器
@post('/add_ser')
def add_ser():
    load_balance_svr_ins.protocol_add_web_svr(request.json)
    return 

# 设置服务器待处理消息数
@post('/set_msg_num')
def set_msg_num():
    load_balance_svr_ins.protocol_set_msg_num(request.json)
    return 

# 客户端websvr连接失败
@post('/web_svr_fail')
def web_svr_fail():
    load_balance_svr_ins.protocol_web_svr_fail(request.json)
    return 

# 获取空闲服务器
@post('/get_min_svr')
def get_min_svr():
    return load_balance_svr_ins.protocol_get_min_svr(request.json)



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








