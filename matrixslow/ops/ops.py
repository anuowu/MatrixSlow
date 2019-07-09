# -*- coding: utf-8 -*-

"""
Created on Wed Jun  5 15:23:01 2019

@author: zhangjuefei
"""
import numpy as np

from core.node import Node


def fill_diagonal(to_be_filled, filler):
    """
    将 filler 矩阵填充在 to_be_filled 的对角线上
    """
    assert to_be_filled.shape[0] / \
        filler.shape[0] == to_be_filled.shape[1] / filler.shape[1]
    n = int(to_be_filled.shape[0] / filler.shape[0])

    r, c = filler.shape
    for i in range(n):
        to_be_filled[i * r:(i + 1) * r, i * c:(i + 1) * c] = filler

    return to_be_filled


class Add(Node):
    """
    矩阵加法
    """

    def compute(self):
        assert len(self.parents) == 2 and self.parents[0].shape(
        ) == self.parents[1].shape()
        self.value = self.parents[0].value + self.parents[1].value

    def get_jacobi(self, parent):
        return np.mat(np.eye(self.dimension()))  # 矩阵之和对其中任一个矩阵的雅可比矩阵是单位矩阵


class MatMul(Node):
    """
    矩阵乘法
    """

    def compute(self):
        assert len(self.parents) == 2 and self.parents[0].shape()[
            1] == self.parents[1].shape()[0]
        self.value = self.parents[0].value * self.parents[1].value

    def get_jacobi(self, parent):
        """
        将矩阵乘法视作映射，求映射对参与计算的矩阵的雅克比矩阵。
        """

        # 很神秘，靠注释说不明白了
        zeros = np.mat(np.zeros((self.dimension(), parent.dimension())))
        if parent is self.parents[0]:
            return fill_diagonal(zeros, self.parents[1].value.T)
        else:
            jacobi = fill_diagonal(zeros, self.parents[0].value)
            row_sort = np.arange(self.dimension()).reshape(
                self.shape()).T.ravel()
            col_sort = np.arange(parent.dimension()).reshape(
                parent.shape()).T.ravel()
            return jacobi[row_sort, :][:, col_sort]


class Dot(Node):
    """
    向量内积
    """

    def compute(self):
        assert len(self.parents) == 2 and self.parents[0].dimension(
        ) == self.parents[1].dimension()
        self.value = self.parents[0].value.T * \
            self.parents[1].value  # 1x1矩阵（标量），为两个父节点的内积

    def get_jacobi(self, parent):
        if parent is self.parents[0]:
            return self.parents[1].value.T
        else:
            return self.parents[0].value.T


class Logistic(Node):
    """
    对向量的分量施加Logistic函数
    """

    def compute(self):
        x = self.parents[0].value
        # 对父节点的每个分量施加Logistic
        self.value = np.mat(
            1.0 / (1.0 + np.power(np.e, np.where(-x > 1e2, 1e2, -x))))

    def get_jacobi(self, parent):
        return np.diag(np.mat(np.multiply(self.value, 1 - self.value)).A1)