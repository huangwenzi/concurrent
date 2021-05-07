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
    , "protocol_weight" : 1         # 请求权重 请求空闲服务器时加待处理消息数
}

# 缓存集群地址
cache_cfg = {
    # 公用配置
    "commun" : {
        "cache_del_time" : 15   # cache数据保留时间（分）
    },
    # 写缓存， 修改数据要在这个cache
    "write" : {
        # 不同配置对应不同的库, 写缓存不可以多个操作同一数据库
        # 修改会广播同步到读缓存
        "1" : { 
            "type" : "write"
            , "svr_id" : 1
            , "host" : "127.0.0.1"
            , "port" : 11100
            , "db_cfg" : "web_svr"
        }
    },
    # 读缓存, 读取数据在这个cache
    "read" : {
        # 不同配置对应不同的库, 写缓存可以多个操作同一数据库
        # 太多读缓存对应同一写缓存，会造成同步压力，酌情添加
        "101" : {
            "type" : "read"
            , "svr_id" : 101
            , "host" : "127.0.0.1"
            , "port" : 11101
            , "db_cfg" : "web_svr"
            , "write_cache" : "1"
        }
    },
}

# 客户端配置
client = {
    "thread_num" : 100
}