import copy
import learningRTA_Symbol.obsTable as obsTable
from learningRTA_Symbol.hypothesis import structHypothesisRTA
from learningRTA_Symbol.teacher import EQs


def learnRTA(targetSys, inputs, upperGuard, stateNum, sampleNum, epsilon, delta):
    mqNum = 0  # 成员查询数
    eqNum = 0  # 等价查询数
    testNum = 0  # 测试次数

    ### 初始化Table
    table, mqNum = obsTable.initTable(inputs, upperGuard, sampleNum, targetSys, mqNum)
    print("***************** init-Table_1 is as follow *******************")
    table.show()

    ### 迭代学习
    equivalent = False
    target = None  # 学习所得系统
    tNum = 1  # 观察表数
    while not equivalent:
        # 处理closed和EvComp，其中EvComp在处理过程中
        flagClosed, closedMove = obsTable.isClosed(table)
        while not flagClosed:
            table, mqNum = obsTable.makeClosed(table, closedMove, inputs, upperGuard, sampleNum, targetSys, mqNum)
            tNum = tNum + 1
            print("***************** closed-Table_" + str(tNum) + " is as follow *******************")
            table.show()
            flagClosed, closedMove = obsTable.isClosed(table)

        ### RTA构建
        hypothesisRTA = structHypothesisRTA(table, inputs)
        print("***************** Hypothesis_" + str(tNum) + " is as follow. *******************")
        hypothesisRTA.show()

        target = copy.deepcopy(hypothesisRTA)

        ### 等价测试
        equivalent, ctx, testNum = EQs(hypothesisRTA, upperGuard, stateNum, epsilon, delta, targetSys, eqNum, testNum)
        eqNum = eqNum + 1
        if not equivalent:
            # 反例显示
            print("***************** counterexample is as follow. *******************")
            print([tw.show() for tw in ctx.tws], ctx.value)
            # 反例处理
            table, mqNum = obsTable.dealCtx(table, ctx, inputs, targetSys, mqNum)
            tNum = tNum + 1
            print("***************** New-Table" + str(tNum) + " is as follow *******************")
            table.show()

    return target, mqNum, eqNum, testNum
