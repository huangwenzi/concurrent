
import time



import client.client_mgr as clientMgrMd






# 创建客户端管理器单例
client_mgr = clientMgrMd.set_ins("1")

while True:
    # 获取参数
    print("客户端数量 执行间隔 执行时间 执行函数 额外参数(',' 分割参数)    例如：2 0.1 60 set 1,2")
    in_str = input("请输入参数：")
    # in_str = "1 0.01 1 get 1"
    in_arr = in_str.split(" ")
    client_mgr.auto(in_arr)