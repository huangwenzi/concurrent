


from concurrent.futures import ThreadPoolExecutor
import time

g_id = 0

def spider(page):
    global g_id
    g_id += 1
    time.sleep(1)
    print("%d : %d"%(page, time.time()))
    return page

t = ThreadPoolExecutor(max_workers=5)
for idx in range(100):
    t.submit(spider, idx)

while True:
    time.sleep(1)
    print("g_id:%d"%(g_id))

















