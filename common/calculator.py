import math

from django.conf import settings


class Calculator(object):
    """
    递减分数算法，参考 Tp0t OJ:
    https://github.com/Tp0t-Team/Tp0tOJ/blob/master/server/utils/calculator/baseCalculator.go

    """

    @staticmethod
    def curve(base_point, count):
        """
        题目分数算法，根据当前答题人数计算题目分数。

        @param base_point: 当前分数
        @param count: 答题人数
        @return: 题目分数
        """
        if count == 0:
            return base_point

        count -= 1
        coefficient = 1.8414 / settings.CHALLENGE.get("HALF_LIFE") * count
        result = math.floor(base_point / (coefficient + math.exp(-coefficient)))
        return result

    @staticmethod
    def get_increment_point(point, index):
        """
        额外奖励分数

        @param point: 题目分数
        @param index: 第 index 位完成题目。
        @return:
        """

        if index == 0:
            return math.floor(point * (1 + float(settings.CHALLENGE.get("FIRST_BLOOD_REWARD"))))
        elif index == 1:
            return math.floor(point * (1 + float(settings.CHALLENGE.get("SECOND_BLOOD_REWARD"))))
        elif index == 2:
            return math.floor(point * (1 + float(settings.CHALLENGE.get("THIRD_BLOOD_REWARD"))))
        else:
            return point

    @staticmethod
    def get_delta_point_for_user(old_point, new_point, index):
        """
        计算需要减去的分数

        @param old_point: 原本的积分
        @param new_point: 新的积分
        @param index: 当前多少位完成
        @return:
        """

        return Calculator.get_increment_point(old_point, index) - Calculator.get_increment_point(new_point, index)
