"""Safe parsing and numeric evaluation of QADL resource expressions."""

from __future__ import annotations

import ast
import math
from collections.abc import Mapping


UNKNOWN_EXPRESSIONS = {"unknown", "tbd", "not-estimated"}


class ExpressionError(ValueError):
    """Raised when a resource expression leaves the supported arithmetic subset."""


_FUNCTIONS = {
    "abs": abs,
    "asin": math.asin,
    "ceil": math.ceil,
    "exp": math.exp,
    "floor": math.floor,
    "log": math.log,
    "log2": math.log2,
    "max": max,
    "min": min,
    "pow": pow,
    "sqrt": math.sqrt,
}
_CONSTANTS = {"e": math.e, "pi": math.pi}
_BINARY_OPERATORS = {
    ast.Add: lambda left, right: left + right,
    ast.Sub: lambda left, right: left - right,
    ast.Mult: lambda left, right: left * right,
    ast.Div: lambda left, right: left / right,
    ast.FloorDiv: lambda left, right: left // right,
    ast.Mod: lambda left, right: left % right,
    ast.Pow: lambda left, right: left**right,
}
_UNARY_OPERATORS = {
    ast.UAdd: lambda value: value,
    ast.USub: lambda value: -value,
}


def is_unknown(expression: object) -> bool:
    return isinstance(expression, str) and expression.strip().lower() in UNKNOWN_EXPRESSIONS


def validate_expression(expression: str, variables: set[str]) -> set[str]:
    """Validate an expression and return the variable names it references."""
    if not isinstance(expression, str) or not expression.strip():
        raise ExpressionError("expression must be a non-empty string")
    if is_unknown(expression):
        return set()
    try:
        tree = ast.parse(expression, mode="eval")
    except SyntaxError as exc:
        raise ExpressionError(f"invalid syntax: {exc.msg}") from exc
    names: set[str] = set()
    _validate_node(tree.body, variables, names)
    return names


def evaluate_expression(expression: str, values: Mapping[str, float]) -> float | None:
    """Evaluate a previously validated expression without Python eval()."""
    if is_unknown(expression):
        return None
    variables = set(values)
    validate_expression(expression, variables)
    tree = ast.parse(expression, mode="eval")
    result = _evaluate_node(tree.body, values)
    if isinstance(result, bool) or not isinstance(result, (int, float)):
        raise ExpressionError("expression did not evaluate to a real number")
    result = float(result)
    if not math.isfinite(result):
        raise ExpressionError("expression evaluated to a non-finite value")
    return result


def _validate_node(node: ast.AST, variables: set[str], names: set[str]) -> None:
    if isinstance(node, ast.Constant):
        if isinstance(node.value, bool) or not isinstance(node.value, (int, float)):
            raise ExpressionError("only real numeric literals are allowed")
        return
    if isinstance(node, ast.Name):
        if node.id not in variables and node.id not in _CONSTANTS:
            raise ExpressionError(f"undeclared symbol: {node.id}")
        if node.id in variables:
            names.add(node.id)
        return
    if isinstance(node, ast.BinOp):
        if type(node.op) not in _BINARY_OPERATORS:
            raise ExpressionError(f"operator is not allowed: {type(node.op).__name__}")
        _validate_node(node.left, variables, names)
        _validate_node(node.right, variables, names)
        return
    if isinstance(node, ast.UnaryOp):
        if type(node.op) not in _UNARY_OPERATORS:
            raise ExpressionError(f"operator is not allowed: {type(node.op).__name__}")
        _validate_node(node.operand, variables, names)
        return
    if isinstance(node, ast.Call):
        if not isinstance(node.func, ast.Name) or node.func.id not in _FUNCTIONS:
            raise ExpressionError("only approved numeric functions are allowed")
        if node.keywords:
            raise ExpressionError("keyword arguments are not allowed")
        for argument in node.args:
            _validate_node(argument, variables, names)
        return
    raise ExpressionError(f"syntax is not allowed: {type(node).__name__}")


def _evaluate_node(node: ast.AST, values: Mapping[str, float]) -> float:
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.Name):
        return values[node.id] if node.id in values else _CONSTANTS[node.id]
    if isinstance(node, ast.BinOp):
        return _BINARY_OPERATORS[type(node.op)](
            _evaluate_node(node.left, values),
            _evaluate_node(node.right, values),
        )
    if isinstance(node, ast.UnaryOp):
        return _UNARY_OPERATORS[type(node.op)](_evaluate_node(node.operand, values))
    if isinstance(node, ast.Call):
        arguments = [_evaluate_node(argument, values) for argument in node.args]
        return _FUNCTIONS[node.func.id](*arguments)
    raise ExpressionError(f"unsupported node: {type(node).__name__}")
