from abstract_state_parity import ParityStaticAnalyzer
from equations import solve_linear_equations
from lattice_creation import create_cartesian_product_two_lattices
from new_summation_analysis import SummationStaticAnalyzer
from typing import Tuple, List
from saav_parser import BOOLCondition, BoolConditionType, ORCondition, ANDCondition, Command, CommandType

class ParitySummationCartesianProduct:
    def __init__(self, variables, coefficiets_range: Tuple[int, int], integer_range: Tuple[int, int]):
        self.variables: List[str] =  variables
        self.parity_analyzer = ParityStaticAnalyzer(variables)
        self.parity_lattice = self.parity_analyzer.lattice_class
        self.summation_analyzer = SummationStaticAnalyzer(variables, coefficiets_range, integer_range)
        self.summation_lattice = self.summation_analyzer.lattice_class
        self.lattice_class = create_cartesian_product_two_lattices(self.parity_lattice, self.summation_lattice) 

    def _evaluate_boolcondition_on_set(self, bool_condition: BOOLCondition, cartesian, set_of_equations) -> bool:
        assert isinstance(cartesian, self.parity_analyzer.tuple_class)
        boolcondition_type: BoolConditionType = bool_condition.boolcondition_type

        if boolcondition_type in {BoolConditionType.B_Even, BoolConditionType.B_Odd}:
            print(f"Checking {bool_condition} on cartesian {cartesian}!")
            if not self.parity_analyzer._evaluate_boolcondition_on_cartesian(bool_condition, cartesian):
                return False
            return True

        elif boolcondition_type == BoolConditionType.B_Sum:
            print(f"Cheking {bool_condition} on Equations!")
            return self.summation_analyzer._evaluate_boolcondition_on_set(bool_condition, set_of_equations)
        
        raise ValueError(f"Ilegal boolcondition: {bool_condition}.")
    
    def _evaluate_andcondition_on_set(self, and_condition: ANDCondition, cartesian, set_of_equations) -> bool:
        assert isinstance(cartesian, self.parity_analyzer.tuple_class)
        for bool_condition in and_condition.conjunction_list:
            if not self._evaluate_boolcondition_on_set(bool_condition, cartesian, set_of_equations):
                return False
        return True

    def _evaluate_orcondition_on_set(self, or_condition: ORCondition, parity_element, set_of_equations: set) -> bool:
        assert isinstance(parity_element, self.parity_lattice)
        for cartesian in parity_element:
            print(f"Verifying {or_condition} for {cartesian} and equations...")
            cartesian_approves_orcondition = False
            for and_condition in or_condition.disjunction_list:
                if self._evaluate_andcondition_on_set(and_condition, cartesian, set_of_equations):
                    cartesian_approves_orcondition = True
                    break
            if not cartesian_approves_orcondition:
                print(f"Assertion failed! Due to: {cartesian}.")
                return False
        return True

    def execute_command_from_abstract_state(self, current_state, command: Command):
        assert isinstance(current_state, self.lattice_class)
        command_type: CommandType = command.command_type
        first_element = current_state.first_element.copy() # type: ignore
        second_element = current_state.second_element.copy() # type: ignore

        if command_type == CommandType.C_Skip:
            pass

        if command.command_type == CommandType.C_Assign_Var:    # i := j
            first_element = self.parity_analyzer.execute_command_from_abstract_state(first_element, command)
            second_element = self.summation_analyzer.execute_command_from_abstract_state(second_element, command)

        if command.command_type == CommandType.C_Assign_Const:    # i := K
            first_element = self.parity_analyzer.execute_command_from_abstract_state(first_element, command)
            second_element = self.summation_analyzer.execute_command_from_abstract_state(second_element, command)
        
        if command.command_type == CommandType.C_Assign_Unknown:    # i := ?
            first_element = self.parity_analyzer.execute_command_from_abstract_state(first_element, command)
            second_element = self.summation_analyzer.execute_command_from_abstract_state(second_element, command)
        
        if command.command_type == CommandType.C_Plus1:     # i := j + 1
            first_element = self.parity_analyzer.execute_command_from_abstract_state(first_element, command)
            second_element = self.summation_analyzer.execute_command_from_abstract_state(second_element, command)

        if command.command_type == CommandType.C_Minus1:    # i := j - 1
            first_element = self.parity_analyzer.execute_command_from_abstract_state(first_element, command)
            second_element = self.summation_analyzer.execute_command_from_abstract_state(second_element, command)
        
        if command.command_type == CommandType.C_Assume:    # assume E
            first_element = self.parity_analyzer.execute_command_from_abstract_state(first_element, command)
            second_element = self.summation_analyzer.execute_command_from_abstract_state(second_element, command)
        
        if command.command_type == CommandType.C_Assert:    # assert ORC
            or_condition: ORCondition = command.command_parameters['ORC']
            set_of_equations = second_element.equations_set.copy() # type: ignore
            solution_without_sigma = solve_linear_equations(self.variables, set_of_equations, [])[0]
            print(f"Got the following solutions: {solution_without_sigma}.")
            if not self._evaluate_orcondition_on_set(or_condition, first_element, set_of_equations):
                print(f"Assretion {or_condition} failed!")
            else:
                print(f"Assretion {or_condition} suceed!")
        
        return self.lattice_class(first_element=first_element, second_element=second_element) # type: ignore


