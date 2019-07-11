# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License

import random

import pytest

import torch
from torch import nn

from utils_nlp.interpreter.Interpreter import (
    Interpreter,
    calculate_regularization,
)


def fixed_length_Phi(x):
    return x[0] * 10 + x[1] * 20 - x[2] * 20 - x[3] * 10


def variable_length_Phi(function):
    return lambda x: (function(x.unsqueeze(0))[0][0])


@pytest.fixture
def fixed_length_interp():
    x = torch.randn(4, 10)
    regular = torch.randn(10)
    return Interpreter(x, fixed_length_Phi, regularization=regular)


@pytest.fixture
def variable_length_interp():
    function = nn.LSTM(10, 10)
    x = torch.randn(4, 10)
    regular = torch.randn(1, 10)
    return Interpreter(
        x, variable_length_Phi(function), regularization=regular
    )


def test_fixed_length_regularization():
    dataset = torch.randn(10, 4, 10)
    regular = calculate_regularization(dataset, fixed_length_Phi)
    assert regular.shape == (10,)


def test_variable_length_regularization():
    function = nn.LSTM(10, 10)
    dataset = [torch.randn(random.randint(5, 9), 10) for _ in range(10)]
    regular = calculate_regularization(
        dataset, variable_length_Phi(function), reduced_axes=[0]
    )
    assert regular.shape == (1, 10)


def test_initialize_interpreter():
    x = torch.randn(4, 10)
    regular = torch.randn(10)
    interpreter = Interpreter(x, fixed_length_Phi, regularization=regular)
    assert interpreter.s == 4
    assert interpreter.d == 10
    assert interpreter.regular.tolist() == regular.tolist()


def test_train_fixed_length_interp(fixed_length_interp):
    fixed_length_interp.optimize(iteration=10)


def test_train_variable_length_interp(variable_length_interp):
    variable_length_interp.optimize(iteration=10)


def test_interpreter_get_simga(fixed_length_interp):
    sigma = fixed_length_interp.get_sigma()
    assert sigma.shape == (4,)
