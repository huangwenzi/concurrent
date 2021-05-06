from urllib import request
import json
import requests
import time
from concurrent.futures import ThreadPoolExecutor,wait



import lib.instance_mgr as instanceMgrMd
import config.net as netCfg



# 线程执行
def thread_fun(client_task, thread_task):
    print("thread_fun ")
    now = time.time()
    stop_time = now + client_task.continued_time
    
    # 获取对应函数
    fun = getattr(client_task, client_task.fun)
    while True:
        client_task.msg_num += 1
        # 执行函数
        fun(thread_task)
        thread_task.run_count += 1
        client_task.run_count += 1
        client_task.msg_num -= 1
        # 等待间隔
        time.sleep(client_task.interval)
        # 退出
        if time.time() >= stop_time:
            break
    # thread_task.show()
    return 0

# 线程任务类
class ThreadTask():
    # 服务器信息
    svr_id = 0              # 服务器id
    host = 0                
    port = 0
    web_svr_path = ""       # 服务器地址 
    
    run_count = 0           # 运行次数
    ret = None              # 返回结果
    
    def __init__(self, data):
        self.svr_id = data["svr_id"]
        self.host = data["host"]
        self.port = data["port"]
        self.web_svr_path = "http://{0}:{1}".format(data["host"], data["port"])
        self.run_count = 0
        self.ret = None
    
    # 打印客户端任务
    def show(self):
        print("thread_task svr_id:%s"%(self.svr_id))
        print("thread_task host:%s"%(self.host))
        print("thread_task port:%s"%(self.port))
        print("thread_task web_svr_path:%s"%(self.web_svr_path))
        print("thread_task run_count:%d"%(self.run_count))
        print("thread_task ret:%d"%(self.ret))

# 客户端任务类
class ClientTask():
    client_num = 0          # 客户端数量
    interval = 0            # 执行间隔
    continued_time = 0      # 持续执行时间
    fun = None              # 执行函数
    fun_agv = []            # 执行函数的参数
    run_count = 0           # 执行次数
    msg_num = 0             # 等待处理的请求   
    
    def __init__(self, param_arr):
        self.client_num = int(param_arr[0])
        self.interval = float(param_arr[1])
        self.continued_time = float(param_arr[2])
        self.fun = param_arr[3]
        self.fun_agv = param_arr[4].split(",")
        self.run_count = 0
        self.msg_num = 0
        
    # 打印客户端任务
    def show(self):
        print("auto client_num:%s"%(self.client_num))
        print("auto interval:%s"%(self.client_num))
        print("auto continued_time:%s"%(self.client_num))
        print("auto fun:%s"%(self.client_num))
        print("auto fun_agv:")
        print(self.fun_agv)
        print("client_task.run_count:%d"%(self.run_count))
        
    # 获取数据
    def get(self, thread_task):
        send_str = "%s/get_val?key=%s"%(thread_task.web_svr_path, self.fun_agv[0])
        ret = request.Request(send_str)
        response = request.urlopen(ret)
        thread_task.ret = response.read().decode('utf-8')
    

# 模拟客户端管理器
class ClientMgr(object):
    load_balance_svr_path = ""       # 负载均衡服务器地址
    client_list = []        # 客户端列表
    t = None                # 线程池
    
    def __init__(self):
        self.client_list = []
        cfg = netCfg.load_balance_cfg
        self.load_balance_svr_path = "http://{0}:{1}".format(cfg["host"], cfg["port"])
        # 初始化线程池
        client_cfg = netCfg.client
        self.t = ThreadPoolExecutor(max_workers=client_cfg["thread_num"])
        
    # 自动执行
    def auto(self, param):
        print("auto begin")
        list = []
        thread_task_list = []
        client_task = ClientTask(param)
        for item in range(client_task.client_num):
            # 是否获取服务器失败
            thread_task = self.get_web_svr()
            if not thread_task:
                print("err get wev_svr fail!")
                continue
            thread_task_list.append(thread_task)
            tmp = self.t.submit(thread_fun, client_task, thread_task)
            list.append(tmp)
        wait(list)
        
        client_task.show()
        self.show_svr_count(thread_task_list)
        print("auto end")
        
    # 展示每个服务器执行数
    def show_svr_count(self, thread_task_list):
        svr_count_map = {}
        for thread_task in thread_task_list:
            if thread_task.svr_id not in svr_count_map:
                svr_count_map[thread_task.svr_id] = 0
            svr_count_map[thread_task.svr_id] += thread_task.run_count
        print("show_svr_count:")
        print(svr_count_map)
    
        
    # 获取websvr信息给客户端任务
    def get_web_svr(self):
        # 从负载均衡获取服务器地址
        send_str = "{0}/get_min_svr".format(self.load_balance_svr_path)
        ret = request.Request(send_str)
        response = request.urlopen(ret)
        read_str = response.read().decode('utf-8')
        # 是否获取失败
        if not read_str:
            return False
        
        data = json.loads(read_str)
        thread_task = ThreadTask(data)
        
        # 尝试连接
        send_str = "%s/check_svr"%(thread_task.web_svr_path)
        ret = request.Request(send_str)
        response = request.urlopen(ret)
        ret = response.read().decode('utf-8')
        if ret != "1":
            # 通知负载均衡
            headers = {'content-type':'application/json'}
            data = {"svr_id" : thread_task.svr_id}
            requests.post("{0}/web_svr_fail".format(self.load_balance_svr_path), data=json.dumps(data),headers=headers)
            return 
        return thread_task
    
        
    
    # 设置数据
    def set(self, key, val):
        headers = {'content-type':'application/json'}
        data = {
            'key': key,
            'val': val
        }
        response = requests.post("set_value_path", data=json.dumps(data),headers=headers)
        # print("send_get key:%s val:%s ret:%s"%(key, val, response.text)) 
    
    
# 获取单例
def get_ins():
    if not instanceMgrMd.instance_mgr.get_ins("clientMgr"):
        client_mgr = ClientMgr()
        instanceMgrMd.instance_mgr.set_ins("clientMgr", client_mgr)
        return client_mgr
    return instanceMgrMd.instance_mgr.get_ins("clientMgr")

