from enum import Enum
from typing import List
from constants import *

class BoolConditionType(Enum):
    B_Even = 1
    B_Odd = 2

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
        
        raise SyntaxError(f"Ilegal BOOLCondition: {self.boolcondition_text}.")
    
    def get_boolcondition_parameters(self) -> dict:
        if self.boolcondition_type == BoolConditionType.B_Even:
            return {"i": self.boolcondition_text[1]}
        
        if self.boolcondition_type == BoolConditionType.B_Odd:
            return {"i": self.boolcondition_text[1]}

    def __repr__(self) -> str:
        if self.boolcondition_type == BoolConditionType.B_Even:
            return f"{EVEN} {self.boolcondition_parameters['i']}"
        
        if self.boolcondition_type == BoolConditionType.B_Odd:
            return f"{ODD} {self.boolcondition_parameters['i']}"
