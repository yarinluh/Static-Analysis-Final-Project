from enum import Enum
from typing import List
from saav_parser.constants import *

class BoolConditionType(Enum):
    B_Even = 1
    B_Odd = 2
    B_Sum = 3

def proper_summation_text(splitted_text: List[str]) -> bool:
    """
    Checks if the splitted text is of the form ['SUM', 'i1', ..., 'in', '=', 'SUM', 'j1', ..., 'jm'].
    """
    if splitted_text[0] != SUM:
        return False
    try:
        second_sum_index = splitted_text[1:].index(SUM) + 1
        if second_sum_index <= 2 or second_sum_index == len(splitted_text)-1 \
             or splitted_text[second_sum_index-1] != EQUAL:
            raise ValueError
    except ValueError:
        return False
    
    text_copy = splitted_text.copy()
    text_copy.remove(SUM)
    text_copy.remove(SUM)
    text_copy.remove(EQUAL)
    return all([element in VARIABLE_NAMES for element in text_copy])


class BOOLCondition:
    def __init__(self, boolcondition_text: str):
        self.boolcondition_text: List[str] = boolcondition_text.split(' ')
        self.boolcondition_type: BoolConditionType = self.get_boolcondition_type()
        self.boolcondition_parameters: dict = self.get_boolcondition_parameters()

    def get_boolcondition_type(self):
        if len(self.boolcondition_text) == 2 and \
            self.boolcondition_text[0] == EVEN and \
            self.boolcondition_text[1] in VARIABLE_NAMES:
            return BoolConditionType.B_Even
        
        if len(self.boolcondition_text) == 2 and \
            self.boolcondition_text[0] == ODD and \
            self.boolcondition_text[1] in VARIABLE_NAMES:
            return BoolConditionType.B_Odd
        
        if proper_summation_text(self.boolcondition_text):
            return BoolConditionType.B_Sum
        
        raise SyntaxError(f"Ilegal BOOLCondition: {self.boolcondition_text}.")
    
    def get_boolcondition_parameters(self) -> dict:
        if self.boolcondition_type == BoolConditionType.B_Even:
            return {"i": self.boolcondition_text[1]}
        
        if self.boolcondition_type == BoolConditionType.B_Odd:
            return {"i": self.boolcondition_text[1]}
        
        if self.boolcondition_type == BoolConditionType.B_Sum:
            first_sum_index = 0
            second_sum_index = self.boolcondition_text[1:].index(SUM) + 1
            return {"i_vec": self.boolcondition_text[first_sum_index+1:second_sum_index-1],
                    "j_vec": self.boolcondition_text[second_sum_index+1:]}
        
        raise SyntaxError(f"Ilegal BOOLCondition: {self.boolcondition_text}.")


    def __repr__(self) -> str:
        if self.boolcondition_type == BoolConditionType.B_Even:
            return f"{EVEN} {self.boolcondition_parameters['i']}"
        
        if self.boolcondition_type == BoolConditionType.B_Odd:
            return f"{ODD} {self.boolcondition_parameters['i']}"
        
        if self.boolcondition_type == BoolConditionType.B_Sum:
            return f"SUM {' '.join(self.boolcondition_parameters['i_vec'])} = SUM {' '.join(self.boolcondition_parameters['j_vec'])}"

        raise SyntaxError(f"Ilegal BOOLCondition: {self.boolcondition_text}.")
