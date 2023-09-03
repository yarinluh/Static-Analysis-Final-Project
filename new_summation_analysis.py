from __future__ import annotations

from typing import List, Tuple, Type, Set, Iterator
from lattice_creation import Lattice
from saav_parser import ECondition, EConditionType, BOOLCondition, BoolConditionType, ANDCondition, ORCondition, Command, CommandType

from equations import clear_variable_from_set, create_equation_class, get_all_possible_equations, solve_linear_equations


def create_available_equations_lattice(EquationClass: Type, coefficiets_range: Tuple[int, int],
                                       integer_range: Tuple[int, int]) -> Type[Lattice]:
    ALL_EQUATIONS: List[EquationClass] = EquationClass.all_equations(minimal_coefficient=coefficiets_range[0],
                                                                     maximal_coefficient=coefficiets_range[1],
                                                                     minimal_integer=integer_range[0],
                                                                     maximal_integer=integer_range[1])
    
    class AvailableEquationsLattice(Lattice):
        def __init__(self, equations_set: Set[EquationClass]):
            self.equations_set: Set[EquationClass] = equations_set

        @staticmethod
        def top() -> AvailableEquationsLattice:
            return AvailableEquationsLattice(equations_set=set())
        
        @staticmethod
        def bottom() -> AvailableEquationsLattice:
            return AvailableEquationsLattice(equations_set=set(ALL_EQUATIONS))
        
        def __eq__(self: AvailableEquationsLattice, other: AvailableEquationsLattice) -> bool:
            return self.equations_set == other.equations_set
        
        def __le__(self: AvailableEquationsLattice, other: AvailableEquationsLattice) -> bool:
            return self.equations_set.issuperset(other.equations_set)
    
        def meet(self: AvailableEquationsLattice, other: AvailableEquationsLattice) -> AvailableEquationsLattice:
            return AvailableEquationsLattice(self.equations_set.union(other.equations_set))
        
        def join(self: AvailableEquationsLattice, other: AvailableEquationsLattice) -> AvailableEquationsLattice:
            return AvailableEquationsLattice(self.equations_set.intersection(other.equations_set))
        
        def __repr__(self) -> str:
            return self.equations_set.__repr__()
        
        def copy(self: AvailableEquationsLattice):
            return AvailableEquationsLattice({s.copy() for s in self.equations_set})
        
        def __iter__(self) -> Iterator[EquationClass]:
            for element in self.equations_set:
                yield element

        def __len__(self) -> int:
            return len(self.equations_set)

    return AvailableEquationsLattice


def ae_example():
    variables = ['x', 'w', 'r']
    AEQ_Lattice: Type[Lattice] = create_available_equations_lattice(variables, (-4, 4), (-5, 5))

    a = AEQ_Lattice.top()
    print(a)
    b = AEQ_Lattice.bottom()
    # print(b)
    # print(len(b))

    # for eq in b.equations_set:
    #     if str(eq) == "":
    #         print(eq, eq.coefficients, eq.m)



class SummationStaticAnalyzer:
    def __init__(self, variables: List[str], coefficiets_range: Tuple[int, int], integer_range: Tuple[int, int]):
        self.variables: List[str] = variables
        self.coefficiets_range = coefficiets_range
        self.integer_range = integer_range
        self.equations_class = create_equation_class(variables)
        self.lattice_class: Type[Lattice] = create_available_equations_lattice(self.equations_class, coefficiets_range, integer_range)

    def _evaluate_econdition_on_set(self, econdition: ECondition, set_of_equations: set) -> set:
        econdition_type: EConditionType = econdition.econdition_type
        new_set: set = set_of_equations.copy()

        if econdition_type  == EConditionType.E_Equal_Var:      # i = j
            i_variable = econdition.econdition_parameters['i']
            j_variable = econdition.econdition_parameters['j']
            if i_variable != j_variable:
                i_variable_index = self.variables.index(i_variable)
                j_variable_index = self.variables.index(j_variable)
                coefficients_for_equation = [0] * len(self.variables)
                coefficients_for_equation[i_variable_index] = 1
                coefficients_for_equation[j_variable_index] = -1
                coefficients_for_equation = tuple(coefficients_for_equation)
                new_set.add(self.equations_class(coefficients=coefficients_for_equation, m=0))

        elif econdition_type == EConditionType.E_Diff_Var:        # i != j
            pass  # TODO can be done better?
        
        elif econdition_type == EConditionType.E_Equal_Const:     # i = K
            i_variable = econdition.econdition_parameters['i']
            K_value = econdition.econdition_parameters['K']
            i_variable_index = self.variables.index(i_variable)
            coefficients_for_equation = [0] * len(self.variables)
            coefficients_for_equation[i_variable_index] = 1
            coefficients_for_equation = tuple(coefficients_for_equation)
            new_set.add(self.equations_class(coefficients=coefficients_for_equation, m=K_value))

        elif econdition_type == EConditionType.E_Diff_Const:      # i != K
            pass  # TODO can be done better?
        
        elif econdition_type == EConditionType.E_True:
            pass
        
        elif econdition_type == EConditionType.E_False:
            new_set = self.lattice_class.bottom().equations_set # type: ignore
        
        else:
            raise ValueError(f"Ilegal econdition: {econdition}.")
        
        return new_set
    
    def _evaluate_boolcondition_on_set(self, bool_condition: BOOLCondition, set_of_equations: set) -> bool:
        boolcondition_type: BoolConditionType = bool_condition.boolcondition_type

        if boolcondition_type == BoolConditionType.B_Sum:
            i_vec: List[str] = bool_condition.boolcondition_parameters['i_vec']
            i_vec_sum = solve_linear_equations(self.variables, set_of_equations, i_vec)[1]
            print(f"Summation result for {i_vec} is: {i_vec_sum}")

            j_vec: List[str] = bool_condition.boolcondition_parameters['j_vec']
            j_vec_sum = solve_linear_equations(self.variables, set_of_equations, j_vec)[1]
            print(f"Summation result for {j_vec} is: {j_vec_sum}")

            return i_vec_sum == j_vec_sum
        
        raise ValueError(f"Ilegal boolcondition: {bool_condition}.")
    
    def _evaluate_andcondition_on_set(self, and_condition: ANDCondition, set_of_equations: set) -> bool:
        for bool_condition in and_condition.conjunction_list:
            if not self._evaluate_boolcondition_on_set(bool_condition, set_of_equations):
                return False
        return True

    def _evaluate_orcondition_on_set(self, or_condition: ORCondition, set_of_equations: set) -> bool:
        for and_condition in or_condition.disjunction_list:
            if self._evaluate_andcondition_on_set(and_condition, set_of_equations):
                return True
        return False

    def execute_command_from_abstract_state(self, current_state, command: Command):
        assert isinstance(current_state, self.lattice_class)
        command_type: CommandType = command.command_type
        new_set: Set[self.equations_class] = current_state.equations_set.copy() # type: ignore

        if command_type == CommandType.C_Skip:
            pass

        if command.command_type == CommandType.C_Assign_Var:    # i := j
            i_variable = command.command_parameters['i']
            j_variable = command.command_parameters['j']
            if i_variable != j_variable:
                new_set = clear_variable_from_set(new_set, i_variable)
                i_variable_index = self.variables.index(i_variable)
                j_variable_index = self.variables.index(j_variable)
                coefficients_for_equation = [0] * len(self.variables)
                coefficients_for_equation[i_variable_index] = 1
                coefficients_for_equation[j_variable_index] = -1
                coefficients_for_equation = tuple(coefficients_for_equation)
                new_set.add(self.equations_class(coefficients=coefficients_for_equation, m=0))

        if command.command_type == CommandType.C_Assign_Const:    # i := K
            i_variable = command.command_parameters['i']
            const = command.command_parameters['K']
            new_set = clear_variable_from_set(new_set, i_variable)
            i_variable_index = self.variables.index(i_variable)
            coefficients_for_equation = [0] * len(self.variables)
            coefficients_for_equation[i_variable_index] = 1
            coefficients_for_equation = tuple(coefficients_for_equation)
            new_set.add(self.equations_class(coefficients=coefficients_for_equation, m=const))
        
        if command.command_type == CommandType.C_Assign_Unknown:    # i := ?
            i_variable = command.command_parameters['i']
            new_set = clear_variable_from_set(new_set, i_variable)
        
        if command.command_type == CommandType.C_Plus1:     # i := j + 1
            i_variable = command.command_parameters['i']
            j_variable = command.command_parameters['j']
            new_set = clear_variable_from_set(new_set, i_variable)
            if i_variable != j_variable:   # TODO is it neccecary?
                i_variable_index = self.variables.index(i_variable)
                j_variable_index = self.variables.index(j_variable)
                coefficients_for_equation = [0] * len(self.variables)
                coefficients_for_equation[i_variable_index] = 1
                coefficients_for_equation[j_variable_index] = -1
                coefficients_for_equation = tuple(coefficients_for_equation)
                new_set.add(self.equations_class(coefficients=coefficients_for_equation, m=1))

        if command.command_type == CommandType.C_Minus1:    # i := j - 1
            i_variable = command.command_parameters['i']
            j_variable = command.command_parameters['j']
            new_set = clear_variable_from_set(new_set, i_variable)
            if i_variable != j_variable:   # TODO is it neccecary?
                i_variable_index = self.variables.index(i_variable)
                j_variable_index = self.variables.index(j_variable)
                coefficients_for_equation = [0] * len(self.variables)
                coefficients_for_equation[i_variable_index] = 1
                coefficients_for_equation[j_variable_index] = -1
                coefficients_for_equation = tuple(coefficients_for_equation)
                new_set.add(self.equations_class(coefficients=coefficients_for_equation, m=-1))
        
        if command.command_type == CommandType.C_Assume:    # assume E
            e_condition: ECondition = command.command_parameters['E']
            new_set = self._evaluate_econdition_on_set(e_condition, new_set)
        
        if command.command_type == CommandType.C_Assert:    # assert ORC
            or_condition: ORCondition = command.command_parameters['ORC']
            solution_without_sigma = solve_linear_equations(self.variables, new_set, [])[0]
            print(f"Got the following solutions: {solution_without_sigma}.")
            if not self._evaluate_orcondition_on_set(or_condition, new_set):
                print(f"Assretion {or_condition} failed!")
        
        # Finally - we explicate.
        print(f"Explicating the set {new_set}.")
        new_set = get_all_possible_equations(EquationClass=self.equations_class,
                                             list_of_equations=list(new_set),
                                             minimal_coefficient=self.coefficiets_range[0],
                                             maximal_coefficient=self.coefficiets_range[1],
                                             minimal_integer=self.integer_range[0],
                                             maximal_integer=self.integer_range[1])
        return self.lattice_class(equations_set=new_set) # type: ignore


