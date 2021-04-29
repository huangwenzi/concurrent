# 网络配置

# web服务器地址
web_svr_cfg = {
    "1" : {
        "svr_id" : 1
        , "host" : "127.0.0.1"
        , "port" : 10001
    },
    "2" : {
        "svr_id" : 2
        , "host" : "127.0.0.1"
        , "port" : 10002
    }
}

# 负载均衡地址
load_balance_cfg = {
    "host" : "127.0.0.1"
    , "port" : 11000
    , "sync_time" : 5 # 同步时间
}

# 客户端配置
client = {
    "thread_num" : 100
}