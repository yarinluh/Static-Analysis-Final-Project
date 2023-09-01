from __future__ import annotations
from lattice_creation import Lattice, create_cartesian_product_lattice, ItemableLattice
from typing import Union, Type, List, Set, Iterator
from saav_parser import ECondition, EConditionType, BOOLCondition, BoolConditionType, ANDCondition, ORCondition, Command, CommandType
from available_expressions import AvailableExpression, solve_linear_equations, explicate_set, clean_variable_from_set

def create_available_expressions_lattice(variables: List[str], maximal_absolute_value_of_integer: int) -> Type[Lattice]:
    ALL_VARIABLES: List[str] = variables
    MAXIMAL_ABSOLUTE_VALUE_OF_INTEGER: int = maximal_absolute_value_of_integer
    TOP_SET = {AvailableExpression(result_variable=result_variable, variable=variable, integer=integer) \
                            for result_variable in ALL_VARIABLES \
                            for variable in ALL_VARIABLES + [None] \
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
    variables = ['x', 'w', 'r']
    maximal_value = 4
    AELattice: Type[Lattice] = create_available_expressions_lattice(variables, maximal_value)

    a = AELattice.top()
    print(a)
    b = AELattice.bottom()
    print(b)
    print(len(b))


class SummationStaticAnalyzer:
    def __init__(self, variables: List[str], maximal_absolute_value_of_integer: int):
        self.variables: List[str] = variables
        self.maximal_absolute_value_of_integer = maximal_absolute_value_of_integer
        self.lattice_class: Type[Lattice] = create_available_expressions_lattice(self.variables, maximal_absolute_value_of_integer)

    def _evaluate_econdition_on_set(self, econdition: ECondition, set_of_expressions: Set[AvailableExpression]) -> Set[AvailableExpression]:
        econdition_type: EConditionType = econdition.econdition_type
        new_set: Set[AvailableExpression] = set_of_expressions.copy()

        if econdition_type  == EConditionType.E_Equal_Var:      # i = j
            i_variable = econdition.econdition_parameters['i']
            j_variable = econdition.econdition_parameters['j']
            if i_variable != j_variable:
                new_set.add(AvailableExpression(i_variable, j_variable, 0))

        elif econdition_type == EConditionType.E_Diff_Var:        # i != j
            pass  # TODO can be done better?
        
        elif econdition_type == EConditionType.E_Equal_Const:     # i = K
            i_variable = econdition.econdition_parameters['i']
            K_value = econdition.econdition_parameters['K']
            new_set.add(AvailableExpression(i_variable, None, K_value))

        elif econdition_type == EConditionType.E_Diff_Const:      # i != K
            pass  # TODO can be done better?
        
        elif econdition_type == EConditionType.E_True:
            pass
        
        elif econdition_type == EConditionType.E_False:
            new_set = self.lattice_class.bottom().expressions_set
        
        else:
            raise ValueError(f"Ilegal econdition: {econdition}.")
        
        return new_set
    
    def _evaluate_boolcondition_on_set(self, bool_condition: BOOLCondition, set_of_expressions: Set[AvailableExpression]) -> bool:
        boolcondition_type: BoolConditionType = bool_condition.boolcondition_type

        if boolcondition_type == BoolConditionType.B_Sum:
            i_vec: List[str] = bool_condition.boolcondition_parameters['i_vec']
            i_vec_sum = solve_linear_equations(self.variables, set_of_expressions, i_vec)[1]
            print(f"Summation result for {i_vec} is: {i_vec_sum}")

            j_vec: List[str] = bool_condition.boolcondition_parameters['j_vec']
            j_vec_sum = solve_linear_equations(self.variables, set_of_expressions, j_vec)[1]
            print(f"Summation result for {j_vec} is: {j_vec_sum}")

            return i_vec_sum == j_vec_sum
        
        raise ValueError(f"Ilegal boolcondition: {bool_condition}.")
    
    def _evaluate_andcondition_on_set(self, and_condition: ANDCondition, set_of_expressions: Set[AvailableExpression]) -> bool:
        for bool_condition in and_condition.conjunction_list:
            if not self._evaluate_boolcondition_on_set(bool_condition, set_of_expressions):
                return False
        return True

    def _evaluate_orcondition_on_set(self, or_condition: ORCondition, set_of_expressions: Set[AvailableExpression]) -> bool:
        for and_condition in or_condition.disjunction_list:
            if self._evaluate_andcondition_on_set(and_condition, set_of_expressions):
                return True
        return False

    def execute_command_from_abstract_state(self, current_state, command: Command):
        assert isinstance(current_state, self.lattice_class)
        command_type: CommandType = command.command_type
        new_set: Set[AvailableExpression] = current_state.expressions_set.copy()

        if command_type == CommandType.C_Skip:
            pass

        if command.command_type == CommandType.C_Assign_Var:    # i := j
            i_variable = command.command_parameters['i']
            j_variable = command.command_parameters['j']
            if i_variable != j_variable:
                new_set = clean_variable_from_set(i_variable, new_set)
                new_set.add(AvailableExpression(i_variable, j_variable, 0))

        if command.command_type == CommandType.C_Assign_Const:    # i := K
            i_variable = command.command_parameters['i']
            const = command.command_parameters['K']
            new_set = clean_variable_from_set(i_variable, new_set)
            new_set.add(AvailableExpression(i_variable, None, const))
        
        if command.command_type == CommandType.C_Assign_Unknown:    # i := ?
            i_variable = command.command_parameters['i']
            new_set = clean_variable_from_set(i_variable, new_set)
        
        if command.command_type == CommandType.C_Plus1:     # i := j + 1
            i_variable = command.command_parameters['i']
            j_variable = command.command_parameters['j']
            new_set = clean_variable_from_set(i_variable, new_set)
            if i_variable != j_variable:
                new_set.add(AvailableExpression(i_variable, j_variable, 1))

        if command.command_type == CommandType.C_Minus1:    # i := j - 1
            i_variable = command.command_parameters['i']
            j_variable = command.command_parameters['j']
            new_set = clean_variable_from_set(i_variable, new_set)
            if i_variable != j_variable:
                new_set.add(AvailableExpression(i_variable, j_variable, -1))
        
        if command.command_type == CommandType.C_Assume:    # assume E
            e_condition: ECondition = command.command_parameters['E']
            new_set = self._evaluate_econdition_on_set(e_condition, new_set)
        
        if command.command_type == CommandType.C_Assert:    # assert ORC
            or_condition: ORCondition = command.command_parameters['ORC']
            solution_without_sigma = solve_linear_equations(self.variables, new_set, [])[0]
            print(f"Got the following solutions: {solution_without_sigma}.")
            if not self._evaluate_orcondition_on_set(or_condition, new_set):
                print(f"Assretion {or_condition} failed!")
        
        # Finally - we explicate and inform the user if he should try with a different number.
        new_set = explicate_set(new_set, maximal_integer=self.maximal_absolute_value_of_integer)
        for integer in {expression.integer for expression in new_set}:
            if abs(integer) > self.maximal_absolute_value_of_integer:
                information = \
                    f"Executing the command {command} on state {current_state} resulted in {new_set}, \
                    but the integer {integer} is more than {self.maximal_absolute_value_of_integer}. \
                    Consider using a higher maximal integer."
                raise RuntimeError(information)
        return self.lattice_class(expressions_set = new_set)

