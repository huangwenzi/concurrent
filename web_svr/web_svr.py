import time
from concurrent.futures import ThreadPoolExecutor
import json
import requests




import lib.number as numMd
import lib.db as dbMd
import lib.instance_mgr as instanceMgrMd
import config.net as netCfg



## websvr服务器
class WebSvr(object):
    svr_id = 0              # 服务器id
    host = ""               
    port = 0
    msg_num = 0             # 待处理消息数
    sync_time = 0           # 同步时间
    load_balance_path = ""  # 同步地址
    t = None                # 线程池，两个，1个连接负载均衡， 1个同步待处理消息数
    
    task_count = 0          # 完成的任务计数
    dbMgr = None            # 数据库单例
    
    def __init__(self, cfg):
        self.svr_id = cfg["svr_id"]
        self.host = cfg["host"]
        self.port = cfg["port"]
        self.msg_num = 0
        load_balance_cfg = netCfg.load_balance_cfg
        self.sync_time = load_balance_cfg["sync_time"]
        self.load_balance_path = "http://{0}:{1}".format(load_balance_cfg["host"], load_balance_cfg["port"])
        self.task_count = 0
        self.t = ThreadPoolExecutor(2)
        self.dbMgr = dbMd.get_ins()
        
        
    ## 获取函数
    # 获取数据
    def get_val(self, query):
        self.msg_num += 1
        try:
            # 模拟计算消耗0.1秒
            numMd.consume_cpu_time_1(0.1)
            # time.sleep(1)
            key = query.key
            val = self.dbMgr.select("test", key) or "None"
            self.msg_num -= 1
            self.task_count += 1
            return val
        except Exception as e:
            print('data_lib getVal, error:', e)
            self.msg_num -= 1
            return "-1"
    
    ## 修改函数
    # 连接负载均衡
    def connect_load_balance_thread(self):
        # 同步函数
        def thread_fun(web_svr):
            # 通知负载均衡，服务器准备就绪
            headers = {'content-type':'application/json'}
            data = {
                'svr_id' : web_svr.svr_id
                , 'host': web_svr.host
                , 'port': web_svr.port
            }
            load_balance_cfg = netCfg.load_balance_cfg
            path = "http://{0}:{1}/add_ser".format(load_balance_cfg["host"], str(load_balance_cfg["port"]))
            while True:
                try:
                    requests.post(path, data=json.dumps(data),headers=headers)
                    # 开启同步线程
                    web_svr.sync_msg_num_thread()
                    # 退出本线程
                    break
                except Exception as e:
                    # 等待一会再重连
                    print("connect_load_balance_thread fail !")
                    time.sleep(10)
        self.t.submit(thread_fun, self)
    
    # 线程同步协议数量
    def sync_msg_num_thread(self):
        # 同步函数
        def thread_fun(web_svr):
            headers = {'content-type':'application/json'}
            while True:
                data = {
                    "svr_id" : web_svr.svr_id
                    , "host" : web_svr.host
                    , "port" : web_svr.port
                    , "msg_num" : web_svr.msg_num
                    , "time" : time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                }
                try:
                    requests.post("{0}/set_msg_num".format(web_svr.load_balance_path), data=json.dumps(data),headers=headers)
                    time.sleep(web_svr.sync_time)
                except Exception as e:
                    print("sync_msg_num_thread fail !")
                    # 重连负载均衡
                    web_svr.connect_load_balance_thread()
                    # 退出本线程
                    break
                
                
        self.t.submit(thread_fun, self)
    
    
# 获取单例
def get_ins(cfg):
    if not instanceMgrMd.instance_mgr.get_ins("web_svr"):
        web_svr = WebSvr(cfg)
        instanceMgrMd.instance_mgr.set_ins("web_svr", web_svr)
        return web_svr
    return instanceMgrMd.instance_mgr.get_ins("web_svr")
