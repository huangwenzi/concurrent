



import lib.instance_mgr as instanceMgrMd

class WebSvr():
    svr_id = 0  
    host = ""
    port = ""
    msg_num = 0     # 待处理消息数
    
    def __init__(self, svr_id, host, port):
        self.svr_id = svr_id
        self.host = host
        self.port = port
        self.msg_num = 0
        
    # 设置待处理消息数
    def get_msg_num(self):
        return self.msg_num
        
    # 设置待处理消息数
    def set_msg_num(self, msg_num):
        self.msg_num = msg_num
        


## 负载均衡服务器
class LoadBalanceSvr():
    svr_list = []       # 服务器列表
    svr_sort_fun = None # 排序函数
    
    def __init__(self):
        self.svr_list = []
        # 预设服务器排序函数
        def sort(x):
            return x.msg_num
        self.svr_sort_fun = sort
        
    ## 获取函数
    # 获取空闲服务器
    def get_min_svr(self):
        web_svr_obj = min(self.svr_list, key=self.svr_sort_fun)
        return web_svr_obj
    
    # 获取web服务器对象
    def get_web_svr(self, svr_id):
        for tmp_web_svr in self.svr_list:
            if tmp_web_svr.svr_id == svr_id:
                return tmp_web_svr
        return False
    
    
    ## 修改函数
    # 设置待处理协议数
    def set_msg_num(self, svr_id, msg_num):
        web_svr = self.get_web_svr(svr_id)
        if web_svr:
            web_svr.set_msg_num(msg_num)
    
    # 添加web_svr
    def add_web_svr(self, svr_id, host, port):
        web_svr = WebSvr(svr_id, host, port)
        self.svr_list.append(web_svr)
    
    
    
    ## 协议处理
    # 添加web_svr
    def protocol_add_web_svr(self, data):
        print("protocol_add_web_svr:")
        print(data)
        
        svr_id = data["svr_id"]
        host = data["host"]
        port = data["port"]
        self.add_web_svr(svr_id, host, port)
        
    # 设置待处理协议数
    def protocol_set_msg_num(self, data):
        print("protocol_set_msg_num:")
        print(data)
        svr_id = data["svr_id"]
        msg_num = data["msg_num"]
        self.set_msg_num(svr_id, msg_num)
        
    # 获取空闲服务器
    def protocol_get_min_svr(self):
        web_svr = self.get_min_svr()
        web_svr.set_msg_num(web_svr.get_msg_num() + 1)
        return web_svr.svr_id

# 获取单例
def get_ins():
    # 创建单例
    if not instanceMgrMd.instance_mgr.get_ins("load_balance_svr"):
        load_balance_svr = LoadBalanceSvr()
        instanceMgrMd.instance_mgr.set_ins("load_balance_svr", load_balance_svr)
        return load_balance_svr
    return instanceMgrMd.instance_mgr.get_ins("load_balance_svr")

