from parity_analysis import PL, create_relational_product_lattice, create_cartesian_product_lattice
from saav_parser import Command, CommandType, ECondition, EConditionType, BOOLCondition, BoolConditionType, ANDCondition, ORCondition
from typing import Set

ParityLattice = PL
ParityCartesianProductLattice = create_cartesian_product_lattice(['x', 'y', 'z'], ParityLattice)
ParityRelationalProductLattice = create_relational_product_lattice(['x', 'y', 'z'], ParityLattice)

current_state: ParityRelationalProductLattice = ParityRelationalProductLattice.top()

def evaluate_econdition_on_cartesian(econdition: ECondition, cartesian: ParityCartesianProductLattice) -> bool:
    econdition_type: EConditionType = econdition.econdition_type

    if econdition_type == EConditionType.E_Equal_Var:
        i_variable = econdition.econdition_parameters['i']
        i_value = cartesian[i_variable]
        j_variable = econdition.econdition_parameters['j']
        j_value = cartesian[j_variable]
        if i_value == ParityLattice.Bottom or j_value == ParityLattice.Bottom:
            return False
        return i_value == ParityLattice.Top or j_value == ParityLattice.Top or i_value == j_value
    
    if econdition_type == EConditionType.E_Diff_Var:
        i_variable = econdition.econdition_parameters['i']
        i_value = cartesian[i_variable]
        j_variable = econdition.econdition_parameters['j']
        j_value = cartesian[j_variable]
        if i_value == ParityLattice.Bottom or j_value == ParityLattice.Bottom:
            return False
        return i_value == ParityLattice.Top or j_value == ParityLattice.Top or i_value != j_value
    
    if econdition_type == EConditionType.E_Equal_Const:
            i_variable = econdition.econdition_parameters['i']
            i_value = cartesian[i_variable]
            K_value = econdition.econdition_parameters['K']
            parity = ParityLattice.Even if K_value % 2 == 0 else ParityLattice.Odd
            if i_value == ParityLattice.Bottom:
                return False
            return i_value == ParityLattice.Top or i_value == parity
    
    if econdition_type == EConditionType.E_Diff_Const:
        i_variable = econdition.econdition_parameters['i']
        i_value = cartesian[i_variable]
        K_value = econdition.econdition_parameters['K']
        parity = ParityLattice.Even if K_value % 2 == 0 else ParityLattice.Odd
        if i_value == ParityLattice.Bottom:
            return False
        return i_value == ParityLattice.Top or i_value != parity
    
    if econdition_type == EConditionType.E_True:
        return True
    
    if econdition_type == EConditionType.E_False:
        return False

def evaluate_boolcondition_on_cartesian(bool_condition: BOOLCondition, cartesian: ParityCartesianProductLattice) -> bool:
    if bool_condition.boolcondition_type == BoolConditionType.B_Even:
            i_variable = bool_condition.boolcondition_parameters['i']
            i_value = cartesian[i_variable]
            return i_value != ParityLattice.Odd
        
    if bool_condition.boolcondition_type == BoolConditionType.B_Odd:
        i_variable = bool_condition.boolcondition_parameters['i']
        i_value = cartesian[i_variable]
        return i_value != ParityLattice.Even

def evaluate_andcondition_on_cartesian(and_condition: ANDCondition, cartesian: ParityCartesianProductLattice) -> bool:
    return all([evaluate_boolcondition_on_cartesian(b, cartesian) for b in and_condition.conjunction_list])

def evaluate_orcondition_on_cartesian(or_condition: ORCondition, cartesian: ParityCartesianProductLattice) -> bool:
    return any([evaluate_andcondition_on_cartesian(a, cartesian) for a in or_condition.disjunction_list])

def execute_command_from_abstract_state(current_state: ParityRelationalProductLattice,
                                        command: Command) -> ParityRelationalProductLattice:
    command_type: CommandType = command.command_type
    new_set: Set[ParityCartesianProductLattice] = set()
    
    if command_type == CommandType.C_Skip:
        return current_state.__copy__()

    if command.command_type == CommandType.C_Assign_Var:    # i := j
        i_variable = command.command_parameters['i']
        j_variable = command.command_parameters['j']
        for cartesian in current_state.set:
            j_value = cartesian[j_variable]
            new_cartesian = cartesian.__copy__()
            new_cartesian[i_variable] = j_value
            new_set.add(new_cartesian)

    if command.command_type == CommandType.C_Assign_Const:    # i := K
        i_variable = command.command_parameters['i']
        const = command.command_parameters['K']
        parity = ParityLattice.Even if const % 2 == 0 else ParityLattice.Odd
        for cartesian in current_state.set:
            new_cartesian = cartesian.__copy__()
            new_cartesian[i_variable] = parity
            new_set.add(new_cartesian)
    
    if command.command_type == CommandType.C_Assign_Unknown:    # i := ?
        i_variable = command.command_parameters['i']
        for cartesian in current_state.set:
            new_cartesian = cartesian.__copy__()
            new_cartesian[i_variable] = ParityLattice.Even
            new_set.add(new_cartesian)
            new_cartesian = cartesian.__copy__()
            new_cartesian[i_variable] = ParityLattice.Odd
            new_set.add(new_cartesian)
    
    if command.command_type == CommandType.C_Plus1 or\
        command.command_type == CommandType.C_Minus1:    # i = j +- 1
        i_variable = command.command_parameters['i']
        j_variable = command.command_parameters['j']
        for cartesian in current_state.set:
            j_value = cartesian[j_variable]
            updated_j_value = ParityLattice.Even if j_value == ParityLattice.Odd else \
                                ParityLattice.Odd if j_value == ParityLattice.Even else \
                                j_value
            new_cartesian = cartesian.__copy__()
            new_cartesian[i_variable] = updated_j_value
            new_set.add(new_cartesian)
    
    if command.command_type == CommandType.C_Assume:    # assume E
        e_condition: ECondition = command.command_parameters['E']
        for cartesian in current_state.set:
            if evaluate_econdition_on_cartesian(e_condition, cartesian):
                new_set.add(cartesian.__copy__())
            else:
                new_set.add(ParityCartesianProductLattice.bottom())
    
    if command.command_type == CommandType.C_Assert:    # assert ORC
        or_condition: ORCondition = command.command_parameters['ORC']
        if all([evaluate_orcondition_on_cartesian(or_condition, cartesian) for cartesian in current_state.set]):
            return current_state.__copy__()
                        
    return ParityRelationalProductLattice(set=new_set)

def example():
    command_texts = [
        'z := ?',
        'x := 0',
        'assume x = 0',
        'assume y = 0',
        'assume x = z',
        'assert (EVEN x  ODD y) (ODD x  ODD y)'
    ]
    for command_text in command_texts:
        print("\n===================================================\n")
        print(f"Performing {command_text} on state: \t{current_state}.")
        current_state = execute_command_from_abstract_state(current_state, Command(command_text))
        print(f"\nGot {len(current_state.set)}-long state: \t{current_state}.")