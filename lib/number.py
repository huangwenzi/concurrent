import time


# 阶乘
def fctorial(n):
    if n <= 1:
        return 1
    return fctorial(n-1)*n

# 小于n的正整数和
def positive_integer_sum(n):
    val = 0
    for idx in range(n):
        val += (idx + 1)
    return val





# 空运行n秒
# 其实没啥用，cpu是占了，但是没有阻碍其它线程调这个函数性能
def consume_cpu_time(consume_time):
    stop_time = time.time() + consume_time
    while True:
        if time.time() >= stop_time:
            return
# 上面的改进版
def consume_cpu_time_1(consume_time):
    # 差不多6500000 ~= 1秒
    positive_integer_sum(int(consume_time * 6500000))