from __future__ import annotations
from lattice_creation import Listable, ListableEnum, ListableLattice, create_tuple_class, create_disjunctive_completion_lattice, create_tuple_subsets_lattice, ListableItemable
from saav_parser import Command, CommandType, ECondition, EConditionType, BOOLCondition, BoolConditionType, ANDCondition, ORCondition
from typing import Set, List, Type
from enum import Enum

class Parity(Listable, Enum, metaclass=ListableEnum):
    EVEN = 0 
    ODD = 1
    
    @staticmethod
    def all_elements() -> List[Parity]:
        return [Parity.EVEN, Parity.ODD]
    
    def copy(self):
        if self == Parity.EVEN:
            return Parity.EVEN
        elif self == Parity.ODD:
            return Parity.ODD
        else:
            raise ValueError(f"Tried to coppy an Ilegal Parity value: {self}.")

def parity_example():
    variables: List[str] = ['x','y','z']

    TupleSubsetLattice: Type[ListableLattice] = create_tuple_subsets_lattice(variables, Parity)

    print(TupleSubsetLattice.top())
    print(len(TupleSubsetLattice.all_elements()))
    

class ParityStaticAnalyzer:
    def __init__(self, variables: List[str]):
        self.variables: List[str] = variables
        self.tuple_class: Type[ListableItemable] = create_tuple_class(variables, Parity)
        self.tuple_subsets_lattice_class: Type[ListableLattice] = create_disjunctive_completion_lattice(self.tuple_class)

    def _evaluate_econdition_on_cartesian(self, econdition: ECondition, cartesian) -> bool:
        assert isinstance(cartesian, self.tuple_class)
        econdition_type: EConditionType = econdition.econdition_type

        if econdition_type in {EConditionType.E_Equal_Var, EConditionType.E_Diff_Var}:  # i = j; i != j
            i_variable = econdition.econdition_parameters['i']
            i_value = cartesian[i_variable]
            j_variable = econdition.econdition_parameters['j']
            j_value = cartesian[j_variable]
            return (econdition_type == EConditionType.E_Equal_Var and i_value == j_value) or \
                   (econdition_type == EConditionType.E_Diff_Var and i_value != j_value)
        
        
        if econdition_type in {EConditionType.E_Equal_Const, EConditionType.E_Diff_Const}:  # i = K; i != K
            i_variable = econdition.econdition_parameters['i']
            i_value = cartesian[i_variable]
            K_value = econdition.econdition_parameters['K']
            parity = Parity.EVEN if K_value % 2 == 0 else Parity.ODD
            return (econdition_type == EConditionType.E_Equal_Const and i_value == parity) or \
                   (econdition_type == EConditionType.E_Diff_Const and i_value != parity)
        
        if econdition_type == EConditionType.E_True:
            return True
        
        if econdition_type == EConditionType.E_False:
            return False
        
        raise ValueError(f"Ilegal econdition: {econdition}.")
    
    def _evaluate_boolcondition_on_cartesian(self, bool_condition: BOOLCondition, cartesian) -> bool:
        assert isinstance(cartesian, self.tuple_class)
        boolcondition_type: BoolConditionType = bool_condition.boolcondition_type

        if boolcondition_type in {BoolConditionType.B_Even, BoolConditionType.B_Odd}:
            i_variable = bool_condition.boolcondition_parameters['i']
            i_value = cartesian[i_variable]
            return (boolcondition_type == BoolConditionType.B_Even and i_value == Parity.EVEN) or \
                   (boolcondition_type == BoolConditionType.B_Odd and i_value == Parity.ODD)
        
        raise ValueError(f"Ilegal boolcondition: {bool_condition}.")
    
    def _evaluate_andcondition_on_cartesian(self, and_condition: ANDCondition, cartesian) -> bool:
        assert isinstance(cartesian, self.tuple_class)
        for bool_condition in and_condition.conjunction_list:
            if not self._evaluate_boolcondition_on_cartesian(bool_condition, cartesian):
                return False
        return True

    def _evaluate_orcondition_on_cartesian(self, or_condition: ORCondition, cartesian) -> bool:
        assert isinstance(cartesian, self.tuple_class)
        for and_condition in or_condition.disjunction_list:
            if self._evaluate_andcondition_on_cartesian(and_condition, cartesian):
                return True
        return False

    def execute_command_from_abstract_state(self, current_state, command: Command):
        assert isinstance(current_state, self.tuple_subsets_lattice_class)
        command_type: CommandType = command.command_type
        new_set: Set[Listable] = set()

        if command_type == CommandType.C_Skip:
            return current_state.copy()

        if command.command_type == CommandType.C_Assign_Var:    # i := j
            i_variable = command.command_parameters['i']
            j_variable = command.command_parameters['j']
            for cartesian in current_state:
                j_value = cartesian[j_variable]
                new_cartesian = cartesian.copy()
                new_cartesian[i_variable] = j_value
                new_set.add(new_cartesian)

        if command.command_type == CommandType.C_Assign_Const:    # i := K
            i_variable = command.command_parameters['i']
            const = command.command_parameters['K']
            parity = Parity.EVEN if const % 2 == 0 else Parity.ODD
            for cartesian in current_state:
                new_cartesian = cartesian.copy()
                new_cartesian[i_variable] = parity
                new_set.add(new_cartesian)
        
        if command.command_type == CommandType.C_Assign_Unknown:    # i := ?
            i_variable = command.command_parameters['i']
            for cartesian in current_state:
                new_cartesian = cartesian.copy()
                new_cartesian[i_variable] = Parity.EVEN
                new_set.add(new_cartesian)
                new_cartesian = cartesian.copy()
                new_cartesian[i_variable] = Parity.ODD
                new_set.add(new_cartesian)
        
        if command.command_type == CommandType.C_Plus1 or\
            command.command_type == CommandType.C_Minus1:    # i = j +- 1
            i_variable = command.command_parameters['i']
            j_variable = command.command_parameters['j']
            for cartesian in current_state:
                j_value = cartesian[j_variable]
                updated_j_value = Parity.EVEN if j_value == Parity.ODD else Parity.ODD
                new_cartesian = cartesian.copy()
                new_cartesian[i_variable] = updated_j_value
                new_set.add(new_cartesian)
        
        if command.command_type == CommandType.C_Assume:    # assume E
            e_condition: ECondition = command.command_parameters['E']
            for cartesian in current_state:
                if self._evaluate_econdition_on_cartesian(e_condition, cartesian):
                    new_set.add(cartesian.copy())
        
        if command.command_type == CommandType.C_Assert:    # assert ORC
            or_condition: ORCondition = command.command_parameters['ORC']
            for cartesian in current_state:
                if not self._evaluate_orcondition_on_cartesian(or_condition, cartesian):
                    print(f"Assertaion {or_condition} failted due to: {cartesian}.")
            return current_state.copy()
                            
        return self.tuple_subsets_lattice_class(set=new_set) # type: ignore


def example():
    command_texts = [
        'z := ?',
        'x := 0',
        'assume x = 0',
        'assume y = 0',
        'assume x = z',
        'assert (EVEN x  ODD y) (ODD x  ODD y)'
    ]

    parity_analyzer: ParityStaticAnalyzer = ParityStaticAnalyzer(variables=['x', 'y', 'z'])
    current_state = parity_analyzer.tuple_subsets_lattice_class.top()

    for command_text in command_texts:
        print("\n===================================================\n")
        print(f"Performing {command_text} on state: \t{current_state}.")
        current_state = parity_analyzer.execute_command_from_abstract_state(current_state, Command(command_text))
        print(f"\nGot {len(current_state.set)}-long state: \t{current_state}.")
        
# example()