from __future__ import annotations
from sympy import solve
from sympy.abc import sigma
from typing import Set, List, Union

class AvailableExpression:
    """
    Represents an expression of the form x = y + m, where:
    x is a variable,
    y is either a variable or None (if x is a constanct, in that case the expression is simple x = m),
    m is an integer,
    """
    def __init__(self, result_variable: str, variable: Union[str, None], integer: int):
        self.result_variable = result_variable
        self.variable = variable
        self.integer = integer
    
    def __eq__(self: AvailableExpression, other: AvailableExpression) -> bool:
        return self.result_variable == other.result_variable \
            and self.variable == other.variable \
            and self.integer == other.integer
                
    def __repr__(self) -> str:
        s = f"{self.result_variable} = "
        if self.variable is not None:
            s += f"{self.variable} "
            s += f"+ {self.integer}" if self.integer >=0 else f"- {-self.integer}"
        else:
            s += f"{self.integer}"
        return s
    
    def __hash__(self) -> int:
        return hash(self.__repr__())
    
    def copy(self) -> AvailableExpression:
        return AvailableExpression(result_variable=self.result_variable,
                                   variable=self.variable,
                                   integer=self.integer)

def convert_expression_to_equation(expression: AvailableExpression) -> str:
    s = f"{expression.result_variable}"
    if expression.variable != None:
        s += f"-{expression.variable}"
    if expression.integer > 0:
        s += f"-{expression.integer}"
    elif expression.integer < 0:
        s += f"+{-expression.integer}"
    return s

def get_summation_equation(variables_to_sum: List[str]):
    s = "sigma"
    for var in variables_to_sum:
        s += f"-{var}"
    return s

def solve_linear_equations(variables: List[str], set_of_expressions: Set[AvailableExpression],
                           variables_to_sum: List[str]):
    equations: List[str] = [convert_expression_to_equation(expression) for expression in set_of_expressions]
    if variables_to_sum != []:
        summation_equation = get_summation_equation(variables_to_sum)
        equations += [summation_equation]
        variables = ['sigma'] + variables
    solution = solve(equations, variables, dict=True)
    if len(solution) == 0:
        return dict(), None
    if len(solution) > 1:
        assert f"More than 1 solution to {equations}! check yourself..."
    solution = solution[0]
    if variables_to_sum == []:
        return solution, None
    return solution, solution[sigma]

def solving_example():
    ae1 = AvailableExpression("x", "y", 1)
    ae2 = AvailableExpression("y", "r", -15)
    ae3 = AvailableExpression("x", "x", 0)
    ae4 = AvailableExpression("r", "r", 0)

    d = solve_linear_equations(['x', 'y', 'z', 'r'], {ae1, ae2, ae3, ae4}, ['x', 'r'])
    print(d)

def clean_variable_from_set(variable: str, set_to_clean: Set[AvailableExpression]):
    """
    Given a set of avilable expressions of the form x = y + m, and a variable r,
    this method cleans from the set expressions that are no longer valid due to change in the value of r,
    meaning expression in which x == r or y == r.
    """
    new_set: Set[AvailableExpression] = set_to_clean.copy()
    for expression in set_to_clean:
        if expression.result_variable == variable or expression.variable == variable:
            new_set.remove(expression)
    return new_set

def explicate_set(set_of_expressions: Set[AvailableExpression], maximal_integer: int):
    """
    The method is given a set of expressions of the form x = y + m.
    For each two expressions that answers the pattern (x = y + n) and (y = z + m),
    the method adds a new expression: (x = z + (m+n)).
    """
    new_set: Set[AvailableExpression] = set_of_expressions.copy()
    for first_expression in set_of_expressions:
        x = first_expression.result_variable
        y = first_expression.variable
        for second_expression in set_of_expressions:
            if second_expression.result_variable != y:
                continue
            z = second_expression.variable
            n = first_expression.integer
            m = second_expression.integer
            if (x == z) or (y == z) or (x == y):  # to avoid infinite loop TODO go over it...
                continue
            if abs(m+n) > maximal_integer:  # TODO check if we can avoid it.
                continue
            new_set.add(AvailableExpression(result_variable=x, variable=z, integer=(m+n)))

    if new_set == set_of_expressions:
        return new_set
    return explicate_set(new_set, maximal_integer)

def aux_examples():
    ae1 = AvailableExpression("a", "b", 1)
    ae2 = AvailableExpression("b", "c", -15)
    ae3 = AvailableExpression("c", "d", 1)
    ae4 = AvailableExpression("d", "e", 0)

    s = {ae1, ae2, ae3, ae4}
    print(s)
    new_s = explicate_set(s, maximal_integer=60)
    # new_s = clean_variable_from_set("b", s)
    print(new_s)
