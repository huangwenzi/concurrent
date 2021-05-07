import time
from concurrent.futures import ThreadPoolExecutor
import json
import requests


import lib.db as dbMd
import lib.instance_mgr as instanceMgrMd
import config.net as netCfg

# cache单元
class CacheVal():
    key = ""
    val = {}
    del_time = 0        # 下次删除的时间
    is_change = False   # 是否有修改
    
    def __init__(self, key):
        self.key = key
        self.val = {}
        self.is_change = False
        
# cache表
class CacheTable():
    table_name = ""
    key_map = {}        # key map
    del_time = 0        # 下次删除的时间
    is_change = False   # 是否有修改
    
    def __init__(self, table_name):
        self.table_name = table_name
        self.key_map = {}
        self.del_time = 0
        self.is_change = False

## cache服务器
class CacheSvr(object):
    cache_type = ""         # cache类型
    svr_id = 0              # 服务器id
    host = ""               
    port = 0
    msg_num = 0             # 待处理消息数
    table_map = {}            # 内存数据 {CacheTable,...}
    # 负载均衡
    sync_time = 0           # 同步时间
    load_balance_path = ""  # 同步地址
    # read_cache
    write_cache_path = ""   # write_cache_path地址
    cache_del_time = 0      # cache删除时间
    # write_cache
    read_cache_map = {}    # read_cache列表 {"svr_id":{:, "host":, "port":}}
    
    t = None                # 线程池
    dbMgr = None            # 数据库单例
    
    def __init__(self, cfg):
        self.cache_type = cfg["type"]
        self.svr_id = cfg["svr_id"]
        self.host = cfg["host"]
        self.port = cfg["port"]
        self.msg_num = 0
        self.table_map = {}
        load_balance_cfg = netCfg.load_balance_cfg
        # 负载均衡
        self.sync_time = load_balance_cfg["sync_time"]
        self.load_balance_path = "http://{0}:{1}".format(load_balance_cfg["host"], load_balance_cfg["port"])
        # read_cache
        if self.cache_type == "read":
            write_cache_cfg = netCfg.cache_cfg["write"][cfg["write_cache"]]
            self.write_cache_path = "http://{0}:{1}".format(write_cache_cfg["host"], write_cache_cfg["port"])
        # write_cache
        self.read_cache_map = {}
        self.t = ThreadPoolExecutor(10)
        self.dbMgr = dbMd.get_ins("")
        # 内存数据删除定时器
        self.cache_del_time = netCfg.cache_cfg["commun"]["cache_del_time"] * 60
        self.del_cache_val_timer()
        self.save_cache_val_timer()
        
        
    # 各种定时器
    # 内存数据删除定时器
    def del_cache_val_timer(self):
        # 同步函数
        def thread_fun(cache_svr):
            while True:
                Now = time.time()
                # 遍历表
                for table_name in cache_svr.table_map:
                    table = cache_svr.table_map[table_name]
                    # 表时间
                    if table.del_time > Now or table.del_time == 0:
                        continue
                    if len(table.key_map) == 0:
                        table.del_time = 0
                        continue
            
                    # 遍历值
                    # 新的 未到的最小删除时间
                    table_time = 0
                    del_key_list = []
                    for key in table.key_map:
                        cache_val = table.key_map[key]
                        # 未到删除时间
                        if cache_val.del_time > Now:
                            # 初始化
                            if table_time == 0 :
                                table_time = cache_val.del_time
                            # 替换更小的
                            if cache_val.del_time < table_time:
                                table_time = cache_val.del_time
                            continue
                        # 到时间
                        del_key_list.append(key)
                    # 修改表时间
                    table.del_time = table_time
                    # 删除到时间的
                    for key in del_key_list:
                        self.del_cache_val(table_name, table[key])
                          
                # 间隔
                time.sleep(30)
        self.t.submit(thread_fun, self)

    # 内存数据写入持久化定时器
    def save_cache_val_timer(self):
        # 只有write_cache使用
        if self.cache_type != "write":
            return
        # 同步函数
        def thread_fun(cache_svr):
            while True:
                # 遍历表
                for table_name in cache_svr.table_map:
                    table = cache_svr.table_map[table_name]
                    # 表是否有修改
                    if ~table.is_change :
                        continue
                    if len(table.key_map) == 0:
                        table.is_change = False
                        continue
            
                    # 遍历值
                    for key in table.key_map:
                        cache_val = table.key_map[key]
                        # 没有修改
                        if ~cache_val.is_change:
                            continue
                        # 有修改
                        # 先写入持久化
                        self.dbMgr.update(table_name, cache_val.val)
                        # 修改数据状态
                        cache_val.is_change = False
                    # 修改表状态
                    table.is_change = False
                          
                # 间隔
                time.sleep(cache_svr.cache_del_time)
        self.t.submit(thread_fun, self)
        
    # 连接负载均衡
    def connect_load_balance_thread(self):
        # read_cache才连负载均衡
        if self.cache_type == "write":
            return
        
        # 同步函数
        def thread_fun(cache_svr):
            # 通知负载均衡，服务器准备就绪
            headers = {'content-type':'application/json'}
            data = {
                "svr_type" : "cache_svr"
                , 'svr_id' : cache_svr.svr_id
                , 'host': cache_svr.host
                , 'port': cache_svr.port
            }
            load_balance_cfg = netCfg.load_balance_cfg
            path = "http://{0}:{1}/add_ser".format(load_balance_cfg["host"], str(load_balance_cfg["port"]))
            while True:
                try:
                    requests.post(path, data=json.dumps(data),headers=headers)
                    # 开启同步线程
                    cache_svr.sync_msg_num_thread()
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
        def thread_fun(cache_svr):
            headers = {'content-type':'application/json'}
            while True:
                data = {
                    "svr_type" : "cache_svr"
                    , 'svr_id' : cache_svr.svr_id
                    , "host" : cache_svr.host
                    , "port" : cache_svr.port
                    , "msg_num" : cache_svr.msg_num
                    , "time" : time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                }
                try:
                    requests.post("{0}/set_msg_num".format(cache_svr.load_balance_path), data=json.dumps(data),headers=headers)
                    time.sleep(cache_svr.sync_time)
                except Exception as e:
                    print("sync_msg_num_thread fail !")
                    # 重连负载均衡
                    cache_svr.connect_load_balance_thread()
                    # 退出本线程
                    break
                   
        self.t.submit(thread_fun, self)

    # 连接write_cache
    def connect_write_cache_thread(self):
        # 就是write_cache
        if self.cache_type == "write":
            return
        
        # 同步函数
        def thread_fun(cache_svr):
            # 通知write_cache，服务器准备就绪
            headers = {'content-type':'application/json'}
            data = {
                'svr_id' : cache_svr.svr_id
                , 'host': cache_svr.host
                , 'port': cache_svr.port
            }
            path = "{0}/add_ser".format(cache_svr.write_cache_path)
            while True:
                try:
                    requests.post(path, data=json.dumps(data),headers=headers)
                    # 开启同步线程
                    cache_svr.sync_msg_num_thread()
                    # 清除本地cache，保证数据同步
                    self.clear_cache()
                    # 退出本线程
                    break
                except Exception as e:
                    # 等待一会再重连
                    print("connect_write_cache_thread fail !")
                    time.sleep(10)
        self.t.submit(thread_fun, self)
        
    # 从数据库获取值
    def select(self, table_name, key):
        info = self.dbMgr.select(table_name, key)
        # 获取失败
        if not info:
            return False
        # 表是否存在
        if table_name not in self.table_map:
            self.table_map[table_name] = {}
        table = self.table_map[table_name]
        # 修改cache_val
        cache_val = CacheVal(key)
        cache_val.val = info
        cache_val.del_time = time.time() + self.cache_del_time
        table[key] = cache_val
        return cache_val

    # val操作
    # 获取值
    def get_val(self, data):
        table_name = data["table_name"]
        key = data["key"]
        # 表不存在
        if table_name not in self.table_map:
            if self.select(table_name, key):
                return False
        table = self.table_map[table_name]
        # key不存在
        if key not in table:
            if self.select(table_name, key):
                return False
        cache_val = table[key]
        # 坑，居然要把json.dumps后的 " 转成 ' 
        ret = json.dumps(cache_val.val)
        ret = ret.replace('"', "'")
        return ret
    
    # write_cache 同步数据
    def sync_val(self, data):
        table_name = data["table_name"]
        key = data["key"]
        val = data["val"]
        # 表不存在
        if table_name not in self.table_map:
            return
        table = self.table_map[table_name]
        # key不存在
        if key not in table:
            return
        # val变化
        cache_val = table[key]
        cache_val.val = val
        cache_val.del_time = time.time() + self.cache_del_time
        cache_val.is_change = True
        # tableb变化
        table.is_change = True
        
    # 修改val
    def change_val(self, data):
        old_val = data["old_val"]
        new_val = data["new_val"]
        val = self.get_val(data)
        # 不存在要新加
        if not val:
            self.dbMgr.update(data["table_name"], new_val)
            return True
        
        # 旧值是否相同
        if val != old_val:
            return False
        data["val"] = new_val
        self.sync_val(data)
        # 同步给read_cache
        self.sync_read_cache(data)
        return True
    
    # 删除cache val
    def del_cache_val(self, table_name, cache_val):
        # 先写入持久化
        self.dbMgr.update(table_name, cache_val.val)
        # 删除cache中的
        del self.table_map[table_name][cache_val.key]
        
        
        
        
    # 清理cache
    def clear_cache(self):
        self.table_map = {}


    # 添加read_cache
    def add_ser(self, data):
        svr_id = data["svr_id"]
        host = data["host"]
        port = data["port"]
        self.read_cache_map[svr_id] = {"svr_id" : svr_id, "host" : host, "port" : port}
            
    # 同步read_cache val修改
    def sync_read_cache(self, data):
        headers = {'content-type':'application/json'}
        send_data=json.dumps(data)
        del_svr = []
        for svr_id in self.read_cache_map:
            read_cache = self.read_cache_map[svr_id]
            try:
                requests.post("http://{0}:{1}/sync_val".format(read_cache["host"], read_cache["port"]), data=send_data,headers=headers)
            except Exception as e:
                # 同步失败
                print("sync_read_cache fail ! svr_id:%s"%(svr_id))
                del_svr.append(svr_id)
        # 删除失败的read_cache
        for svr_id in del_svr:
            del self.read_cache_map[svr_id]
        
# 获取单例
def get_ins(cfg):
    if not instanceMgrMd.instance_mgr.get_ins("cache_svr"):
        cache_svr = CacheSvr(cfg)
        instanceMgrMd.instance_mgr.set_ins("cache_svr", cache_svr)
        return cache_svr
    return instanceMgrMd.instance_mgr.get_ins("cache_svr")












