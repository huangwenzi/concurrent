from bottle import default_app, run, get, post, request
from beaker.middleware import SessionMiddleware
import requests
import sys
import json

import web_svr.data_lib as dataLibMd

# 负载均衡地址
_add_svr_path = "http://127.0.0.1:11000/addSer"


# 服务器
# 设置session参数
session_opts = {
    'session.type': 'file',
    'session.cookie_expires': 3600,
    'session.data_dir': '/tmp/sessions/simple',
    'session.auto': True
}

# 协议
# 获取值
@get('/getVal')
def getVal():
    dataLibMd
    try:
        # 短暂休眠，模拟计算消耗
        time.sleep(0.001)
        key = request.query.key
        val = dbMgr.get_val(key) or "None"
        return val
    except Exception as e:
        print('getVal, error:', e.value)
        return "-1"





# 函数主入口
def svr_run():
    port = int(sys.argv[1])
    app_argv = SessionMiddleware(default_app(), session_opts)
    # # 通知负载均衡，服务器准备就绪
    # headers = {'content-type':'application/json'}
    # data = {
    #     'ip': "127.0.0.1",
    #     'port': port
    # }
    # response = requests.post(_add_svr_path, data=json.dumps(data),headers=headers)
    run(app=app_argv, host='0.0.0.0', port=port, debug=True, reloader=True)

svr_run()








