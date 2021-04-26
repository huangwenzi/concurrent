from bottle import default_app, run, get, post, request
from beaker.middleware import SessionMiddleware


import web_svr.data_lib as dataLibMd
import config.net as netCfg
import config.db_cfg as dbCfg
import lib.db as dbMd


# 协议
# 获取值
@get('/getVal')
def getVal():
    return dataLibMd.getVal(request.query)




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
    # cfg = netCfg.web_svr_cfg[sys.argv[1]]
    cfg = netCfg.web_svr_cfg["1"]
    app_argv = SessionMiddleware(default_app(), session_opts)
    # # 通知负载均衡，服务器准备就绪
    # headers = {'content-type':'application/json'}
    # data = {
    #     'ip': "127.0.0.1",
    #     'port': port
    # }
    # response = requests.post(_add_svr_path, data=json.dumps(data),headers=headers)
    run(app=app_argv, host=cfg["host"], port=cfg["port"], debug=True, reloader=True)
    
    # 初始化db
    dbMd.set_ins(dbCfg.db_map["web_svr"])
    

svr_run()








