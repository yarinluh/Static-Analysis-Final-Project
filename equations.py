from __future__ import annotations

from typing import List
from sympy import solve
from sympy.abc import sigma
import numpy as np
from itertools import product
from typing import Set, List, Union, Type, Tuple


def create_equation_class(variables: List[str]):
    """
    Given a list of variables (v1, v2, ..., vn), creates a class of which each element contains:
    - A vector (a1, ..., an) of integer coefficients.
    - An integer m.
    This element represents the equation:
    a1*v1 + a2*v2 + ... + an*vn - m = 0
    """
    class Equation:
        def __init__(self, coefficients: Tuple, m: int):
            assert len(variables) == len(coefficients)
            self.variables: List[str] = variables
            self.coefficients = coefficients
            self.m = m

        def __eq__(self: Equation, other: Equation) -> bool:
            return self.variables == other.variables and \
                self.coefficients == other.coefficients and \
                self.m == other.m
        
        def __contains__(self, item) -> bool:
            assert item in self.variables
            index_of_item = self.variables.index(item)
            return self.coefficients[index_of_item] != 0
        
        def get_coefficient(self, var: str) -> int:
            assert var in self.variables
            var_index = self.variables.index(var)
            return self.coefficients[var_index]
        
        def set_coefficient(self, var: str, coeff: int) -> None:
            assert var in self.variables
            var_index = self.variables.index(var)
            coeff_list = list(self.coefficients)
            coeff_list[var_index] = coeff
            self.coefficients = tuple(coeff_list)
        
        def __repr__(self) -> str:
            s = ""
            for var, coeff in zip(self.variables, self.coefficients):
                if coeff > 0:
                    s += f"+ {coeff}*{var} "
                elif coeff < 0:
                    s += f"- {-coeff}*{var} "
            integer_string: str = f"- {self.m}" if self.m > 0 else f"+ {-self.m}" if self.m < 0 else ""
            if s == "":  # all coefficients are 0.
                return integer_string
            if s[0] == "+":
                s = s[2:]
            s += integer_string
            return s
        
        def __hash__(self) -> int:
            return hash(self.__repr__())
        
        def copy(self) -> Equation:
            return Equation(coefficients=self.coefficients, m=self.m)
        
        @staticmethod
        def all_equations(minimal_coefficient: int, maximal_coefficient: int,
                          minimal_integer: int, maximal_integer: int) -> List[Equation]:
            all_coefficients = np.arange(minimal_coefficient, maximal_coefficient + 1)
            all_vectors = product(all_coefficients, repeat=len(variables))
            all_integers = np.arange(minimal_integer, maximal_integer + 1)
            
            l: List[Equation] = []
            for vector in all_vectors:
                for integer in all_integers:
                    l.append(Equation(vector, integer))

            return l

        
    return Equation
        

def get_contradicting_equations(equation, minimal_integer: int, maximal_integer: int) -> set:
    """
    For instance, if the equation is x + y + 1 = 0,
    returns every equation of the form x + y + _ = 0, where _ is a constant different than 1;
    ans also every equation of the form -x - y - _ = 0, correspondly.
    """
    s = set()
    for integer in range(minimal_integer, maximal_integer + 1):
        if integer == equation.m:
            continue
        new_equation = equation.copy()
        new_equation.m = integer
        s.add(new_equation)
        
        flipped_equation = new_equation.copy()
        for var in flipped_equation.variables:
            flipped_equation.set_coefficient(var, -flipped_equation.get_coefficient(var))
        flipped_equation.m *= (-1)
        s.add(flipped_equation)

    return s

def get_all_possible_equations(EquationClass: Type, list_of_equations: list,
                               minimal_coefficient: int, maximal_coefficient: int,
                               minimal_integer: int, maximal_integer: int) -> set:
    """
    TODO lower running times!
    """
    assert all(isinstance(eq, EquationClass) for eq in list_of_equations)
    if len(list_of_equations) == 0:
        return set()
    variables = list_of_equations[0].variables
    list_of_equations_as_strings = [str(eq) for eq in list_of_equations if str(eq) != ""]

    all_equations: Set[EquationClass] = set(EquationClass.all_equations(minimal_coefficient, maximal_coefficient,
                                                                        minimal_integer, maximal_integer))
    try_to_solve_list_of_equations = solve(list_of_equations_as_strings, variables, dict=True)
    if len(try_to_solve_list_of_equations) == 0:
        """
        Assuming list_of_equation has a solution, so does list_of_equations_with_sigme.
        So first we check if list_of_equation has a solution, and if not - we don't change the set.
        TODO should we do so? or maybe return an empty set? of the set of all possible equations??
        TODO consult with Raz...? He says we should return bottom (= set of everythin
        """
        return all_equations

    result: Set[EquationClass] = set(list_of_equations).intersection(all_equations)
    equations_to_skip: Set[EquationClass] = set()

    for equation in all_equations:
        for var in {v for v in variables if v in equation}:
            if all([var not in original_equation for original_equation in list_of_equations]):
                equations_to_skip.add(equation)
                break

    for equation in all_equations:

        if str(equation) == "" or str(equation) == "0":  # all coeffieients & integers are 0, or the equations is "0 = 0".
            continue
        if equation in equations_to_skip:
            continue
        if equation in result:  # if equation is one of the original equations...
            contradicting_equations = get_contradicting_equations(equation, minimal_integer, maximal_integer)
            equations_to_skip.union(contradicting_equations)
            continue

        equation_with_sigma = f"{sigma} - ({equation})"
        list_of_equations_with_sigme = list_of_equations_as_strings + [equation_with_sigma]
        solution = solve(list_of_equations_with_sigme, [sigma] + variables, dict=True)[0]
        # TODO can be shoreter if we use the solution without sigma... But see if solve takes all the time...
        if solution[sigma] == 0:
            result.add(equation)
            contradicting_equations = get_contradicting_equations(equation, minimal_integer, maximal_integer)
            equations_to_skip.union(contradicting_equations)

    return result

def equation_example():
    vars = ['x', 'y', 'z']
    Equation = create_equation_class(vars)
    print(Equation.all_equations(-1, 1, -2, 2))
    eq1 = Equation((1, 0, -1), 1)
    print(eq1)
    eq2 = Equation((0, 1, -1), 0)
    print(eq2)
    solution = solve([str(eq) for eq in [eq1, eq2]], vars, dict=True)
    print(solution)
    print(get_all_possible_equations(Equation, [eq1, eq2], -1, 1, -2, 2))

def clear_variable_from_set(set_of_equations: set, variable_to_clear: str):
    new_set: set = set_of_equations.copy()
    for equation in set_of_equations:
        if variable_to_clear in equation:
            new_set.remove(equation)
    return new_set

def replace_variable_with_another(set_of_equations: set, new_variable: str, old_variable: str):
    """
    This function is used in case we want to add an assginment: new_variable := old_variable.
    It takes every equation that has old_variable and replaced it with new_variable.

    For instnace, if we had an equation x + y = 15 and now we assigned i := y, we should add x + i = 15.

    TODO:
        For now, it is not implementesd on assignments like new_variable := old_variable + 1.
        It can be done in a similar way - just need to make sure the new equation does not pass the limit of integers.
    """
    new_set: set = set_of_equations.copy()
    for equation in set_of_equations:
        if old_variable in equation:
            old_coefficient = equation.get_coefficient(old_variable)
            assert equation.get_coefficient(new_variable) == 0
            new_equation = equation.copy()
            new_equation.set_coefficient(old_variable, 0)
            new_equation.set_coefficient(new_variable, old_coefficient)
            new_set.add(new_equation)
    return new_set

def get_summation_equation(variables_to_sum: List[str]):
    s = "sigma"
    for var in variables_to_sum:
        s += f"-{var}"
    return s

def solve_linear_equations(variables: List[str], set_of_equations: set, variables_to_sum: List[str]):
    equations: List[str] = [str(expression) for expression in set_of_equations if str(expression) != ""]
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