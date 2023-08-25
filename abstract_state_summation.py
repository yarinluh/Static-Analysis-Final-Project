from __future__ import annotations
from lattice_creation import Lattice, create_cartesian_product_lattice, ItemableLattice
from typing import Union, Type, List, Set, Iterator
from saav_parser import ECondition, EConditionType, BOOLCondition, BoolConditionType, ANDCondition, ORCondition, Command, CommandType

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

def create_available_expressions_lattice(variables: Set[str], maximal_absolute_value_of_integer: int) -> Type[Lattice]:
    ALL_VARIABLES: Set[str] = variables
    MAXIMAL_ABSOLUTE_VALUE_OF_INTEGER: int = maximal_absolute_value_of_integer
    TOP_SET = {AvailableExpression(result_variable=result_variable, variable=variable, integer=integer) \
                            for result_variable in ALL_VARIABLES \
                            for variable in ALL_VARIABLES \
                            for integer in range(-MAXIMAL_ABSOLUTE_VALUE_OF_INTEGER, MAXIMAL_ABSOLUTE_VALUE_OF_INTEGER+1) \
                                if result_variable != variable}

    class AELattice(Lattice):
        def __init__(self, expressions_set: Set[AvailableExpression]):
            self.expressions_set: Set[AvailableExpression] = expressions_set

        @staticmethod
        def top() -> AELattice:
            return AELattice(expressions_set=set())
        
        @staticmethod
        def bottom() -> AELattice:
            return AELattice(expressions_set=TOP_SET)
        
        def __eq__(self: AELattice, other: AELattice) -> bool:
            return self.expressions_set == other.expressions_set
        
        def __le__(self: AELattice, other: AELattice) -> bool:
            return self.expressions_set.issuperset(other.expressions_set)
    
        def meet(self: AELattice, other: AELattice) -> AELattice:
            return AELattice(self.expressions_set.union(other.expressions_set))
        
        def join(self: AELattice, other: AELattice) -> AELattice:
            return AELattice(self.expressions_set.intersection(other.expressions_set))
        
        def __repr__(self) -> str:
            return self.expressions_set.__repr__()
        
        def copy(self: AELattice):
            return AELattice({s.copy() for s in self.expressions_set})
        
        def __iter__(self) -> Iterator[AvailableExpression]:
            for element in self.expressions_set:
                yield element

        def __len__(self) -> int:
            return len(self.expressions_set)

    return AELattice

def ae_exmple():
    variables = {'x', 'w', 'r'}
    maximal_value = 4
    AELattice: Type[Lattice] = create_available_expressions_lattice(variables, maximal_value)

    a = AELattice.top()
    print(a)
    b = AELattice.bottom()
    print(b)
    print(len(b))


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

def explicate_set(set_of_expressions: Set[AvailableExpression]):
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
            new_set.add(AvailableExpression(result_variable=x, variable=z, integer=(m+n)))
    return new_set

def aux_examples():
    ae1 = AvailableExpression("x", "y", 1)
    ae2 = AvailableExpression("y", "z", -15)
    ae3 = AvailableExpression("x", None, 5)
    ae4 = AvailableExpression("r", "x", 0)

    s = {ae1, ae2, ae3, ae4}
    print(s)
    # new_s = explicate_set(s)
    new_s = clean_variable_from_set("x", s)
    print(new_s)

class SummationStaticAnalyzer:
    def __init__(self, variables: Set[str], maximal_absolute_value_of_integer: int):
        self.variables: Set[str] = variables
        self.maximal_absolute_value_of_integer = maximal_absolute_value_of_integer
        self.lattice_class: Type[Lattice] = create_available_expressions_lattice(self.variables, maximal_absolute_value_of_integer)

    def _evaluate_econdition_on_cartesian(self, econdition: ECondition, cartesian):
        assert isinstance(cartesian, self.lattice_class)
        econdition_type: EConditionType = econdition.econdition_type

        if econdition_type  == EConditionType.E_Equal_Var:      # i = j
            pass

        if econdition_type == EConditionType.E_Diff_Var:        # i != j
            pass
        
        if econdition_type == EConditionType.E_Equal_Const:     # i = K
            pass

        if econdition_type == EConditionType.E_Diff_Const:      # i != K
            pass
        
        if econdition_type == EConditionType.E_True:
            pass
        
        if econdition_type == EConditionType.E_False:
            pass
        
        raise ValueError(f"Ilegal econdition: {econdition}.")
    
    def _evaluate_boolcondition_on_cartesian(self, bool_condition: BOOLCondition, cartesian) -> bool:
        assert isinstance(cartesian, self.lattice_class)
        boolcondition_type: BoolConditionType = bool_condition.boolcondition_type

        if boolcondition_type == BoolConditionType.B_Sum:
            pass
        
        raise ValueError(f"Ilegal boolcondition: {bool_condition}.")
    
    def _evaluate_andcondition_on_cartesian(self, and_condition: ANDCondition, cartesian) -> bool:
        assert isinstance(cartesian, self.lattice_class)
        for bool_condition in and_condition.conjunction_list:
            if not self._evaluate_boolcondition_on_cartesian(bool_condition, cartesian):
                return False
        return True

    def _evaluate_orcondition_on_cartesian(self, or_condition: ORCondition, cartesian) -> bool:
        assert isinstance(cartesian, self.lattice_class)
        for and_condition in or_condition.disjunction_list:
            if self._evaluate_andcondition_on_cartesian(and_condition, cartesian):
                return True
        return False

    def execute_command_from_abstract_state(self, current_state, command: Command):
        assert isinstance(current_state, self.lattice_class)
        command_type: CommandType = command.command_type
        new_set: Set[AvailableExpression] = current_state.expressions_set.copy()

        if command_type == CommandType.C_Skip:
            pass

        if command.command_type == CommandType.C_Assign_Var:    # i := j
            pass

        if command.command_type == CommandType.C_Assign_Const:    # i := K
            pass
        
        if command.command_type == CommandType.C_Assign_Unknown:    # i := ?
            pass
        
        if command.command_type == CommandType.C_Plus1:     # i := j + 1
            pass

        if command.command_type == CommandType.C_Minus1:    # i := j - 1
            pass
        
        if command.command_type == CommandType.C_Assume:    # assume E
            pass
        
        if command.command_type == CommandType.C_Assert:    # assert ORC
            pass
        
        # Finally - we explicate and inform the user if he should try with a different number.
        new_set = explicate_set(new_set)
        for integer in {expression.integer for expression in new_set}:
            if abs(integer) > self.maximal_absolute_value_of_integer:
                information = \
                    f"Executing the command {command} on state {current_state} resulted in {new_set}, \
                    but the integer {integer} is more than {self.maximal_absolute_value_of_integer}. \
                    Consider using a higher maximal integer."
                assert information
        return self.lattice_class(expressions_set = new_set)

