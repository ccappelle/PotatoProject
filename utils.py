import numpy as np


def identity(x):
    return x


def sigmoid(x):
    return 2.0 / (1.0 + np.exp(-x)) - 1.0


def positive_sigmoid(x):
    return (1 + sigmoid(x)) * 0.5


def neg_abs(x):
    return -np.abs(x)


def neg_square(x):
    return -np.square(x)


def sqrt_abs(x):
    return np.sqrt(np.abs(x))


def neg_sqrt_abs(x):
    return -sqrt_abs(x)


def mean_abs(x):
    return np.mean(np.abs(x))


def std_abs(x):
    return np.std(np.abs(x))


def normalize(x):
    x -= np.min(x)
    x /= np.max(x)
    x = np.nan_to_num(x)
    x *= 2
    x -= 1
    return x
