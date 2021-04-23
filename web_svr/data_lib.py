

# 数据处理
def getVal(query):
    dataLibMd
    try:
        # 短暂休眠，模拟计算消耗
        time.sleep(0.001)
        key = query.key
        val = dbMgr.get_val(key) or "None"
        return val
    except Exception as e:
        print('getVal, error:', e.value)
        return "-1"