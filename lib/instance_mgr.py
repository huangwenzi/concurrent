



#　单例管理器
class InstanceMgr():
    # 单例字典
    instance = {}

    # 初始化
    def __init__(self):
        self.instance = {}

    # 获取单例
    def get_ins(self, name):
        if name in self.instance:
            return self.instance[name]
        return None
    
    # 设置单例
    def set_ins(self, name, obj):
        self.instance[name] = obj

instance_mgr = InstanceMgr()