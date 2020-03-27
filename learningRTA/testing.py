import math
import random
from common.timedWord import TimedWord
from Automata.system import systemOutput


# 反例类
class Ctx(object):
    def __init__(self, tws, value):
        self.tws = tws
        self.value = value


# 根据分布随机采样测试
def randomTesting(hypothesis, upperGuard, stateNum, epsilon, delta, targetSys, eqNum, testNum):
    flag = True  # 等价True，不等价False
    sample = []
    ctx = Ctx(sample, None)
    testSum = (math.log(1 / epsilon) + math.log(2) * (eqNum + 1)) / delta  # 人为定义最大测试次数
    i = 1
    while i <= testSum:
        testNum += 1
        sample = sampleGeneration(hypothesis, upperGuard, stateNum)
        value = getHpyValue(sample, hypothesis)
        realValue = systemOutput(sample, targetSys)
        if value != realValue:
            flag = False
            ctx = Ctx(sample, realValue)
            return flag, ctx, testNum
        i += 1
    return flag, ctx, testNum


# 根据设定的分布随机采样
def sampleGeneration(hypothesis, upperGuard, stateNum):
    sample = []
    length = math.ceil(abs(random.normalvariate(0, 2 * stateNum + 1)))
    for i in range(length):
        input = hypothesis.inputs[random.randint(0, len(hypothesis.inputs) - 1)]
        time = random.randint(0, upperGuard * 2 - 1) / 2
        temp = TimedWord(input, time)
        sample.append(temp)
    return sample


# 获得假设下sample的值
def getHpyValue(sample, hypothesis):
    curStateNow = hypothesis.initState
    if len(sample) == 0:
        if hypothesis.initState in hypothesis.acceptStates:
            return 1
        else:
            return 0
    else:
        for tw in sample:
            for tran in hypothesis.trans:
                if tran.source == curStateNow and tran.isPass(tw):
                    curStateNow = tran.target
                    break
            if curStateNow == hypothesis.sinkState:
                return -1
        if curStateNow in hypothesis.acceptStates:
            return 1
        else:
            return 0
