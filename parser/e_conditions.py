from enum import Enum
from typing import List
from constants import *

class EConditionType(Enum):
    E_Equal_Var = 1
    E_Diff_Var = 2
    E_Equal_Const = 3
    E_Diff_Const = 4
    E_True = 5
    E_False = 6


class ECondition:
    def __init__(self, econdition_text: List[str]):
        self.econdition_text: List[str] = econdition_text
        self.econdition_type: EConditionType = self.get_econtition_type()
        self.econdition_parameters: dict = self.get_econdition_parameters()

    def get_econdition_type(self) -> EConditionType:
        if len(self.econdition_text) == 3 and \
            self.econdition_text[0] in VARIABLE_NAMES and \
            self.econdition_text[1] == EQUAL and \
            self.econdition_text[2] in VARIABLE_NAMES:
            return EConditionType.E_Equal_Var
        
        if len(self.econdition_text) == 3 and \
            self.econdition_text[0] in VARIABLE_NAMES and \
            self.econdition_text[1] == NOT_EQUAL and \
            self.econdition_text[2] in VARIABLE_NAMES:
            return EConditionType.E_Diff_Var
        
        if len(self.econdition_text) == 3 and \
            self.econdition_text[0] in VARIABLE_NAMES and \
            self.econdition_text[1] == EQUAL and \
            self.econdition_text[2].isdigit():
            return EConditionType.E_Equal_Const
        
        if len(self.econdition_text) == 3 and \
            self.econdition_text[0] in VARIABLE_NAMES and \
            self.econdition_text[1] == NOT_EQUAL and \
            self.econdition_text[2].isdigit:
            return EConditionType.E_Diff_Const

        if self.econdition_text == ['TRUE']:
            return EConditionType.E_True
        
        if self.econdition_text == ['FALSE']:
            return EConditionType.E_False
        
        raise SyntaxError(f"Ilegal ECondition: {self.econdition_text}!")

    def get_econtition_parameters(self) -> dict:
        if self.econdition_type == EConditionType.E_Equal_Var or \
            self.econdition_type == EConditionType.E_Diff_Var:
            return {"i": self.command_text[0],
                    "j": self.command_text[2]}
        
        if self.econdition_type == EConditionType.E_Equal_Const or \
            self.econdition_type == EConditionType.E_Diff_Const:
            return {"i": self.command_text[0],
                    "K": self.command_text[2]}
        
        if self.econdition_type == EConditionType.E_True or \
            self.econdition_type == EConditionType.E_False:
            return {}


