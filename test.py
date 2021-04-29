

## 线程池测试
# from concurrent.futures import ThreadPoolExecutor
# import time
# g_id = 0

# def spider(page):
#     global g_id
#     g_id += 1
#     time.sleep(1)
#     print("%d : %d"%(page, time.time()))
#     return page

# t = ThreadPoolExecutor(max_workers=5)
# for idx in range(100):
#     t.submit(spider, idx)

# while True:
#     time.sleep(1)
#     print("g_id:%d"%(g_id))



# ## 压力测试
# import time
# import config.db_cfg as dbCfg
# import lib.db as dbMd
# cfg = dbCfg.db_map["web_svr"]
# db_mgr = dbMd.DbMgr(cfg)
# now = time.time()
# for idx in range(10000):
#     db_mgr.select("test", 1)
# print("selevt consume:{0}".format(time.time() - now))

# now = time.time()
# for idx in range(10000):
#     info = {
#         "id" : idx
#         , "val" : idx
#         , "name" : str(idx)
#     }
#     db_mgr.update("test", info)
# print("update consume:{0}".format(time.time() - now))

# # 电脑太垃圾了 写每秒才50
# # selevt consume:0.9806616306304932
# # update consume:219.1766881942749










