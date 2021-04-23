
# 阶乘
def fctorial(n):
    if n <= 1:
        return 1
    return fctorial(n-1)*n

# 小于n的正整数和
def positive_integer_sum(n):
    if n <= 1:
        return 1
    return positive_integer_sum(n-1) + n