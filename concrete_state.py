from saav_parser.constants import VARIABLE_NAMES
from saav_parser import Command, CommandType, ECondition, EConditionType, ORCondition, \
    ANDCondition, BOOLCondition, BoolConditionType

UNKNOWN = "Unknown"
UNDEFINED = "Undefined"

class ConcreteState:
    """
    Represents a map from each variable in VARIABLE_NAMES to one of the following:
    1. "Unkown" (the variable is defined, but its value is unknown).
    2. A natural number (the variable is defind, and its value is known)
    3. "Undefined" (the variable is not defined).
    """
    def __init__(self):
        self.mapping = {v: UNDEFINED for v in VARIABLE_NAMES}

    def __getitem__(self, variable):
        return self.mapping[variable]
    
    def __setitem__(self, variable, value: int):
        if variable not in VARIABLE_NAMES:
            raise ValueError(f"{variable} is not a Variable!")
        if value not in {UNKNOWN, UNDEFINED} and not isinstance(value, int):
            raise ValueError(f"{value} is not a legal value!")
        self.mapping[variable] = value

    def __copy__(self):
        new_state = ConcreteState()
        for v in VARIABLE_NAMES:
            new_state[v] = self[v]
        return new_state

    def __repr__(self):
        mapping_for_print = {v: self.mapping[v] for v in VARIABLE_NAMES if self.mapping[v] != UNDEFINED}
        return str(mapping_for_print)

    def evaluate_boolcondition(self, bool_condition: BOOLCondition) -> bool:
        if bool_condition.boolcondition_type == BoolConditionType.B_Even:
            i_variable = bool_condition.boolcondition_parameters['i']
            i_value = self[i_variable]
            return isinstance(i_value, int) and i_value % 2 == 0
        
        if bool_condition.boolcondition_type == BoolConditionType.B_Odd:
            i_variable = bool_condition.boolcondition_parameters['i']
            i_value = self[i_variable]
            return isinstance(i_value, int) and i_value % 2 != 0

    def evaluate_andcondition(self, and_condition: ANDCondition) -> bool:
        return all([self.evaluate_boolcondition(b) for b in and_condition.conjunction_list])
    
    def evaluate_orcondition(self, or_condition: ORCondition) -> bool:
        return any([self.evaluate_andcondition(a) for a in or_condition.disjunction_list])
    
    def evaluate_econdition(self, e_condition: ECondition) -> bool:
        if e_condition.econdition_type == EConditionType.E_Equal_Var:
            i_variable = e_condition.econdition_parameters['i']
            i_value = self[i_variable]
            j_variable = e_condition.econdition_parameters['j']
            j_value = self[j_variable]
            return isinstance(i_value, int) and isinstance(j_value, int) and i_value == j_value
        
        if e_condition.econdition_type == EConditionType.E_Diff_Var:
            i_variable = e_condition.econdition_parameters['i']
            i_value = self[i_variable]
            j_variable = e_condition.econdition_parameters['j']
            j_value = self[j_variable]
            return isinstance(i_value, int) and isinstance(j_value, int) and i_value != j_value
        
        if e_condition.econdition_type == EConditionType.E_Equal_Const:
            i_variable = e_condition.econdition_parameters['i']
            i_value = self[i_variable]
            K_value = e_condition.econdition_parameters['K']
            return isinstance(i_value, int) and i_value == K_value
        
        if e_condition.econdition_type == EConditionType.E_Diff_Const:
            i_variable = e_condition.econdition_parameters['i']
            i_value = self[i_variable]
            K_value = e_condition.econdition_parameters['K']
            return isinstance(i_value, int) and i_value != K_value

        if e_condition.econdition_type == EConditionType.E_True:
            return True
        
        if e_condition.econdition_type == EConditionType.E_False:
            return False

    def is_possible_to_execute_command(self, command: Command) -> bool:
        if command.command_type == CommandType.C_Assign_Var or \
            command.command_type == CommandType.C_Plus1 or \
            command.command_type == CommandType.C_Minus1:
            j_variable = command.command_parameters['j']
            j_value = self[j_variable]
            return isinstance(j_value, int)
                            
        if command.command_type == CommandType.C_Assume:    # assume E
            e_condition: ECondition = command.command_parameters['E']
            return self.evaluate_econdition(e_condition)

        return True

    def execute_command_from_concrete_state(self, command: Command):
        new_state = self.__copy__()

        if command.command_type == CommandType.C_Skip:      # skip
            pass

        if command.command_type == CommandType.C_Assign_Var:    # i := j
            i_variable = command.command_parameters['i']
            j_variable = command.command_parameters['j']
            j_value = new_state[j_variable]
            new_state[i_variable] = j_value
            pass

        if command.command_type == CommandType.C_Assign_Const:    # i := K
            i_variable = command.command_parameters['i']
            const = command.command_parameters['K']
            new_state[i_variable] = const
            pass
        
        if command.command_type == CommandType.C_Assign_Unknown:    # i := ?
            i_variable = command.command_parameters['i']
            new_state[i_variable] = UNKNOWN
            pass
        
        if command.command_type == CommandType.C_Plus1:    # i := j + 1
            i_variable = command.command_parameters['i']
            j_variable = command.command_parameters['j']
            j_value = new_state[j_variable]            
            new_state[i_variable] = j_value + 1
            pass
        
        if command.command_type == CommandType.C_Minus1:    # i := j - 1
            i_variable = command.command_parameters['i']
            j_variable = command.command_parameters['j']
            j_value = new_state[j_variable]
            new_state[i_variable] = j_value - 1
            pass

        if command.command_type == CommandType.C_Assume:    # assume E
            pass
        
        if command.command_type == CommandType.C_Assert:    # assert ORC
            or_condition: ORCondition = command.command_parameters['ORC']
            if self.evaluate_orcondition(or_condition) == False:
                return None

        return new_state

