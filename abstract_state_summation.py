from __future__ import annotations
from lattice_creation import Lattice, create_cartesian_product_lattice, ItemableLattice
from typing import Union, Type, List
from saav_parser import ECondition, EConditionType, BOOLCondition, BoolConditionType, ANDCondition, ORCondition, Command, CommandType

TOP_ELEMENT = "TOP_ELEMENT"
BOTTOM_ELEMENT = "BOTTOM_ELEMENT"

class AvailableExpression(Lattice):
    def __init__(self, unknown_variable: Union[str, None], integer: int):
        self.unknown_variable = unknown_variable
        self.integer = integer

    @staticmethod
    def top() -> AvailableExpression:
        return AvailableExpression(TOP_ELEMENT, 0)
    
    @staticmethod
    def bottom() -> AvailableExpression:
        return AvailableExpression(BOTTOM_ELEMENT, 0)
    
    def __eq__(self: AvailableExpression, other: AvailableExpression) -> bool:
        return self.unknown_variable == other.unknown_variable and self.integer == other.integer
    
    def __le__(self: AvailableExpression, other: AvailableExpression) -> bool:
        return self == AvailableExpression.bottom() or other == AvailableExpression.top() or self == other
    
    def meet(self: AvailableExpression, other: AvailableExpression) -> AvailableExpression:
        if self <= other:
            return self
        if other <= self:
            return other
        return AvailableExpression.bottom()
    
    def join(self: AvailableExpression, other: AvailableExpression) -> AvailableExpression:
        if self <= other:
            return other
        if other <= self:
            return self
        return AvailableExpression.top()
    
    def __repr__(self) -> str:
        if self == AvailableExpression.top():
            return TOP_ELEMENT
        if self == AvailableExpression.bottom():
            return BOTTOM_ELEMENT
        extra = f" + {self.integer}" if self.integer > 0 else f" - {-self.integer}" if self.integer < 0 else ""
        return f"<{self.unknown_variable}" + extra + ">"
    
def summation_exmple():
    variables = ['x', 'w', 'r']
    SummationLattice: Type[ItemableLattice] = create_cartesian_product_lattice(variables, AvailableExpression)

    a = SummationLattice.top()
    print(a)
    a['x'] = AvailableExpression('w', 5)
    print(a)

summation_exmple()

class SummationStaticAnalyzer:
    def __init__(self, variables: List[str]):
        self.variables: List[str] = variables
        self.lattice_class: Type[ItemableLattice] = create_cartesian_product_lattice(variables, AvailableExpression)

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




