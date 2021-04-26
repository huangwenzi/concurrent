import time


import lib.number as numMd
import lib.db as dbMd

# 数据单例
dbMgr = dbMd.get_ins()

# 数据处理
def getVal(query):
    try:
        # 模拟计算消耗0.1秒
        numMd.positive_integer_sum(0.1)
        key = query.key
        val = dbMgr.select("test", key) or "None"
        return val
    except Exception as e:
        print('data_lib getVal, error:', e)
        return "-1"