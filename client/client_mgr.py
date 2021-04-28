from urllib import request, parse
import json
import requests
import time
from concurrent.futures import ThreadPoolExecutor,wait



import lib.instance_mgr as instanceMgrMd
import config.net as netCfg

# getValue地址
get_value_path = "http://127.0.0.1:11000/getVal"
# getValue地址
set_value_path = "http://127.0.0.1:11000/setVal"

# 线程执行
def thread_fun(client_mgr, client_task):
    print("thread_fun ")
    now = time.time()
    stop_time = now + client_task.continued_time
    # 执行次数
    run_count = 0
    
    # 获取对应函数
    fun = getattr(client_mgr, client_task.fun)
    while True:
        # 执行函数
        fun(*client_task.fun_agv)
        run_count += 1
        client_task.run_count += 1
        # 等待间隔
        time.sleep(client_task.interval)
        # 退出
        if time.time() >= stop_time:
            break
    print("auto client_num:%s"%(client_task.client_num))
    print("auto interval:%s"%(client_task.interval))
    print("auto continued_time:%s"%(client_task.continued_time))
    print("auto fun:%s"%(client_task.fun))
    print("auto fun_agv:")
    print(client_task.fun_agv)
    print("auto run_count:%s\n\n"%(run_count))
    return 0

class ClientTask(object):
    client_num = 0          # 客户端数量
    interval = 0            # 执行间隔
    continued_time = 0      # 持续执行时间
    fun = None              # 执行函数
    fun_agv = []            # 执行函数的参数
    run_count = 0           # 执行次数
    
    def __init__(self, param_arr):
        self.client_num = int(param_arr[0])
        self.interval = float(param_arr[1])
        self.continued_time = float(param_arr[2])
        self.fun = param_arr[3]
        self.fun_agv = param_arr[4].split(",")
        self.run_count = 0
    

# 模拟客户端管理器
class ClientMgr(object):
    web_svr_path = ""       # 服务器地址
    client_list = []        # 客户端列表
    t = None                # 线程池
    
    def __init__(self, cfg_name):
        self.client_list = []
        cfg = netCfg.web_svr_cfg[cfg_name]
        self.web_svr_path = "http://{0}:{1}".format(cfg["host"], cfg["port"])
        # 初始化线程池
        client_cfg = netCfg.client
        self.t = ThreadPoolExecutor(max_workers=client_cfg["thread_num"])
        
    # 自动执行
    def auto(self, param):
        print("auto begin")
        client_task = ClientTask(param)
        list = []
        for item in range(client_task.client_num):
            tmp = self.t.submit(thread_fun, self, client_task)
            list.append(tmp)
        wait(list)
        print("client_task.run_count:%d"%(client_task.run_count))
        print("auto end")
            
        
    # 获取数据
    def get(self, key):
        send_str = "%s/get_val?key=%s"%(self.web_svr_path, key)
        ret = request.Request(send_str)
        response = request.urlopen(ret)
        read_str = response.read().decode('utf-8')
        # print("send_get key:%s ret:%s"%(key, read_str)) 
    
    # 设置数据
    def set(self, key, val):
        headers = {'content-type':'application/json'}
        data = {
            'key': key,
            'val': val
        }
        response = requests.post(set_value_path, data=json.dumps(data),headers=headers)
        # print("send_get key:%s val:%s ret:%s"%(key, val, response.text)) 
    
    
# 创建单例
def set_ins(cfg_name):
    client_mgr = ClientMgr(cfg_name)
    instanceMgrMd.instance_mgr.set_ins("clientMgr", client_mgr)
    return client_mgr
# 获取单例
def get_ins():
    instanceMgrMd.instance_mgr.get_ins("clientMgr")

