from Automata.system import systemOutput
from learningRTA_Symbol.testing import randomTesting


# 成员查询
def TQs(tws, targetSys):
    value = systemOutput(tws, targetSys)
    return value


# 等价查询
def EQs(hypothesis, upperGuard, stateNum, epsilon, delta, targetSys, eqNum, testNum):
    equivalent, ctx, testNum = randomTesting(hypothesis, upperGuard, stateNum, epsilon, delta, targetSys, eqNum, testNum)
    return equivalent, ctx, testNum
