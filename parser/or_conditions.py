from typing import List

class ORCondition:
    def __init__(self, orcondition_text: str):
        self.orcondition_text: str = orcondition_text
        self.disjunction_list: List[ANDCondition] = self.get_disjunction_list()

    def get_disjuction_list(self) -> List[ANDCondition]:
        if self.orcondition_text[-1] != ')':
            raise SyntaxError(f"Ilegal ORCondition: {self.orconditioext}.")
        
        pasred_text: List[str] = self.orcondition_text.split(')')[:-1]
        pasred_text = [word.strip() for word in pasred_text]
        if not all([word.startswith('(') for word in pasred_text]):
            raise SyntaxError(f"Ilegal ORCondition: {pasred_text}.")
        else:
            parsed_text = [word[1:] for word in parsed_text]

        return [ANDCondition(word) for word in parsed_text]
