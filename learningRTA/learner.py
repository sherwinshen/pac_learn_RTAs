import copy
import learningRTA.obsTable as obsTable
from learningRTA.teacher import EQs
from learningRTA.hypothesis import structDiscreteRTA, structHypothesisRTA
from learningRTA.testing import getHpyValue, Ctx
from Automata.system import systemOutput
from learningRTA.computingError import buildCanonicalRTA, buildMergeRTA, buildComplementRTA, distanceMetric, getMinCtxList


def learnRTA(targetSys, inputs, upperGuard, stateNum, epsilon, delta):
    mqNum = 0  # 成员查询数
    eqNum = 0  # 等价查询数
    testNum = 0  # 测试次数

    tempSys = copy.deepcopy(targetSys)
    targetFullSys = buildCanonicalRTA(tempSys, upperGuard)

    ### 初始化Table
    table, mqNum = obsTable.initTable(inputs, targetSys, mqNum)
    print("***************** init-Table_1 is as follow *******************")
    table.show()

    ### 迭代学习
    equivalent = False
    tNum = 1  # 观察表数
    stableHpy = None  # 学习所得系统
    metric = 1
    while not equivalent:
        # 属性验证
        prepared = obsTable.isPrepared(table)
        while not prepared:
            # 处理closed
            flagClosed, closedMove = obsTable.isClosed(table)
            if not flagClosed:
                table, mqNum = obsTable.makeClosed(table, inputs, closedMove, targetSys, mqNum)
                tNum = tNum + 1
                print("***************** closed-Table_" + str(tNum) + " is as follow *******************")
                table.show()
            # 处理consistent
            flagConsistent, consistentAdd = obsTable.isConsistent(table)
            if not flagConsistent:
                table, mqNum = obsTable.makeConsistent(table, consistentAdd, targetSys, mqNum)
                tNum = tNum + 1
                print("***************** consistent-Table_" + str(tNum) + " is as follow *******************")
                table.show()
            prepared = obsTable.isPrepared(table)

        ### RTA构建
        # 迁移为时间点的RTA
        discreteRTA = structDiscreteRTA(table, inputs)
        print("***************** discreteRTA_" + str(tNum) + " is as follow. *******************")
        discreteRTA.showDiscreteRTA()
        # 迁移为时间区间的RTA
        hypothesisRTA = structHypothesisRTA(discreteRTA, upperGuard)
        print("***************** Hypothesis_" + str(tNum) + " is as follow. *******************")
        hypothesisRTA.showRTA()

        if stableHpy is not None:
            flag, ctx, mqNum, metric = hpyCompare(stableHpy, hypothesisRTA, upperGuard, targetSys, targetFullSys, mqNum, metric)
            if flag:
                ### 等价测试
                equivalent, ctx, testNum = EQs(hypothesisRTA, upperGuard, stateNum, epsilon, delta, targetSys, eqNum, testNum)
                eqNum = eqNum + 1
                stableHpy = copy.deepcopy(hypothesisRTA)
            else:
                print("Comparator找到反例！！！")
                equivalent = False
        else:
            ### 等价测试
            equivalent, ctx, testNum = EQs(hypothesisRTA, upperGuard, stateNum, epsilon, delta, targetSys, eqNum, testNum)
            eqNum = eqNum + 1
            stableHpy = copy.deepcopy(hypothesisRTA)

            # 计算当前假设与目标系统的距离度量
            mergeSys = buildMergeRTA(targetFullSys, hypothesisRTA)
            complementSys = buildComplementRTA(mergeSys, upperGuard)
            metric = distanceMetric(complementSys)

        if not equivalent:
            # 反例显示
            print("***************** counterexample is as follow. *******************")
            print([tw.show() for tw in ctx.tws], ctx.value)
            # 反例处理
            table, mqNum = obsTable.dealCtx(table, ctx, hypothesisRTA, targetSys, mqNum)
            tNum = tNum + 1
            print("***************** New-Table" + str(tNum) + " is as follow *******************")
            table.show()

    return stableHpy, mqNum, eqNum, testNum


# 距离度量和假设比较器
def hpyCompare(stableHpy, hypothesisRTA, upperGuard, targetSys, targetFullSys, mqNum, metric):
    print("Stable hypothesis metric: ", metric)

    # 计算当前假设与目标系统的距离度量
    mergeSys = buildMergeRTA(targetFullSys, hypothesisRTA)
    complementSys = buildComplementRTA(mergeSys, upperGuard)
    newMetric = distanceMetric(complementSys)
    print("Current hypothesis metric: ", newMetric)


    # 计算两个假设的最小区分序列
    mergeRTA = buildMergeRTA(stableHpy, hypothesisRTA)
    complementRTA = buildComplementRTA(mergeRTA, upperGuard)
    compareTrace = getMinCtxList(complementRTA, upperGuard)

    # makePic.makeLearnedRTA(stableHpy, "../test", '/前一个假设')
    # makePic.makeLearnedRTA(hypothesisRTA, "../test", '/当前假设')
    # makePic.makeComplementRTA(complementRTA, "../test", '/组合自动机')

    flag = True
    ctx = Ctx([], 0)
    for trace in compareTrace:
        value = getHpyValue(trace, hypothesisRTA)
        realValue = systemOutput(trace, targetSys)
        mqNum += 1
        if value != realValue:
            flag = False
            ctx = Ctx(trace, realValue)
            break
    if flag and newMetric > metric:
        return "Metric Error"
    return flag, ctx, mqNum, newMetric
