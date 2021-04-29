import time
from concurrent.futures import ThreadPoolExecutor,wait
import json
import requests
import sys



import lib.number as numMd
import lib.db as dbMd
import lib.instance_mgr as instanceMgrMd
import config.net as netCfg

# 数据单例
dbMgr = dbMd.get_ins()

## websvr服务器
class WebSvr(object):
    svr_id = 0              # 服务器id
    msg_num = 0             # 待处理消息数
    sync_time = 0           # 同步时间
    load_balance_path = ""  # 同步地址
    
    task_count = 0          # 完成的任务计数
    
    def __init__(self, cfg):
        self.svr_id = int(cfg["svr_id"])
        self.msg_num = 0
        load_balance_cfg = netCfg.load_balance_cfg
        self.sync_time = load_balance_cfg["sync_time"]
        self.load_balance_path = "http://{0}:{1}/set_msg_num".format(load_balance_cfg["host"], load_balance_cfg["port"])
        self.task_count = 0
        
        
    ## 获取函数
    # 获取数据
    def get_val(self, query):
        self.msg_num += 1
        try:
            # 模拟计算消耗0.1秒
            numMd.consume_cpu_time_1(0.1)
            # time.sleep(1)
            key = query.key
            val = dbMgr.select("test", key) or "None"
            self.msg_num -= 1
            self.task_count += 1
            return val
        except Exception as e:
            print('data_lib getVal, error:', e)
            self.msg_num -= 1
            return "-1"
    
    ## 修改函数
    # 线程同步协议数量
    def sync_msg_num_thread(self):
        # 同步函数
        def thread_fun(web_svr):
            headers = {'content-type':'application/json'}
            while True:
                data = {
                    "svr_id" : web_svr.svr_id
                    , "msg_num" : web_svr.msg_num
                    , "time" : time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                }
                requests.post(web_svr.load_balance_path, data=json.dumps(data),headers=headers)
                time.sleep(web_svr.sync_time)
                
        t = ThreadPoolExecutor(1)
        t.submit(thread_fun, self)
    
    
# 获取单例
def get_ins():
    if not instanceMgrMd.instance_mgr.get_ins("web_svr"):
        cfg = netCfg.web_svr_cfg[sys.argv[1]]
        web_svr = WebSvr(cfg)
        instanceMgrMd.instance_mgr.set_ins("web_svr", web_svr)
        return web_svr
    return instanceMgrMd.instance_mgr.get_ins("web_svr")
