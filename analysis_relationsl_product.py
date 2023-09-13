from __future__ import annotations
from typing import Tuple, List, Type, Set, Iterator
from lattice_creation import Lattice
from analysis_parity import ParityStaticAnalyzer
from analysis_summation import SummationStaticAnalyzer
from saav_parser import Command, CommandType, ORCondition, BOOLCondition, BoolConditionType, ANDCondition
from equations import solve_linear_equations


def create_relational_combine_product(tuple_class, available_equations_lattice: Type[Lattice]) -> Type[Lattice]:
    """
    The first element is a class representing tuples of the form (p1, ..., pn) where pi is the parity of pn.
    The second element is a class representing a set of linear equations.
    The created lattice's elements are sets of tuples (pairty_element, equations_element),
        parity_element is an element of tuple_class,
        equations_element is an element of available_equations_lattice.

    The top element is a set of 2^n tuples - all possible parity vectors, and paired with no equations.
    The bottom element is an empty set - representing that there is no legal concrete assignment.
    The join() function is union of sets, and meet() is intersection.
    """
    class relational_product(Lattice):
        def __init__(self, parity_equations_tuples_set: Set[Tuple[tuple_class, available_equations_lattice]]):
            self.tuples_set: Set[Tuple[tuple_class, available_equations_lattice]] = parity_equations_tuples_set

        @staticmethod
        def top() -> relational_product:
            all_possible_tuples: List[tuple_class] = tuple_class.all_elements()
            empty_equations_set: available_equations_lattice = available_equations_lattice.top()
            all_tuples = {(parity_tuple, empty_equations_set) for parity_tuple in all_possible_tuples}
            return relational_product(parity_equations_tuples_set=all_tuples)
        
        @staticmethod
        def bottom() -> relational_product:
            return relational_product(parity_equations_tuples_set=set())
        
        def __eq__(self: relational_product, other: relational_product) -> bool:
            return self.tuples_set == other.tuples_set
        
        def __le__(self: relational_product, other: relational_product) -> bool:
            """
            First, we define le((parity_element1, equations_element1), (parity_element2, equations_element2)).
            This is True iff parity_elemenet1 == parity_element2 and equations_element1 <= equations_element2.
            Here "<=" is the le() relations from available_equations_lattice, which translates to issuperset().

            Now we define self <= other iff every tuple t1 in self.tuples_set,
            has a tuple t2 in other.tuples_set,
            such that le(t1, t2).
            """
            for (parity_element1, equations_element1) in self.tuples_set:
                found_bigger_element = False
                for (parity_element2, equations_element2) in other.tuples_set:
                    if parity_element1 == parity_element2 and equations_element1 <= equations_element2:
                        found_bigger_element = True
                        break
                if not found_bigger_element:
                    return False
            return True
        
        def meet(self: relational_product, other: relational_product) -> relational_product:
            if self <= other:
                return self
            if other <= self:
                return other
            return relational_product(parity_equations_tuples_set=self.tuples_set.intersection(other.tuples_set))
        
        def join(self: relational_product, other: relational_product) -> relational_product:
            if self <= other:
                return other
            if other <= self:
                return self
            return relational_product(parity_equations_tuples_set=self.tuples_set.union(other.tuples_set))
        
        def __repr__(self) -> str:
            set_of_strings = {f"<{parity_element.__repr__()}, {equations_element.__repr__()}>"
                              for (parity_element, equations_element) in self.tuples_set}
            return set_of_strings.__repr__()
        
        def copy(self: relational_product):
            return relational_product(parity_equations_tuples_set={t.copy() for t in self.tuples_set}) # type: ignore
        
        def __iter__(self) -> Iterator[Tuple[tuple_class, available_equations_lattice]]:
            for t in self.tuples_set:
                yield t

    return relational_product

class ParitySummationRelationalProduct:
    def __init__(self, variables, coefficiets_range: Tuple[int, int], integer_range: Tuple[int, int]):
        self.variables: List[str] =  variables

        self.parity_analyzer = ParityStaticAnalyzer(variables)
        self.tuple_class = self.parity_analyzer.tuple_class

        self.summation_analyzer = SummationStaticAnalyzer(variables, coefficiets_range, integer_range)
        self.summation_lattice = self.summation_analyzer.lattice_class

        self.lattice_class = create_relational_combine_product(self.tuple_class, self.summation_lattice)


    def _evaluate_boolcondition_on_tuple(self, bool_condition: BOOLCondition, parity_element, equations_element) -> bool:
        assert isinstance(parity_element, self.tuple_class)
        assert isinstance(equations_element, self.summation_lattice)
        boolcondition_type: BoolConditionType = bool_condition.boolcondition_type

        if boolcondition_type in {BoolConditionType.B_Even, BoolConditionType.B_Odd}:
            if not self.parity_analyzer._evaluate_boolcondition_on_cartesian(bool_condition, parity_element):
                return False
            return True

        elif boolcondition_type == BoolConditionType.B_Sum:
            set_of_equations = equations_element.equations_set # type: ignore
            return self.summation_analyzer._evaluate_boolcondition_on_set(bool_condition, set_of_equations)
        
        raise ValueError(f"Ilegal boolcondition: {bool_condition}.")
    
    def _evaluate_andcondition_on_tuple(self, and_condition: ANDCondition, parity_element, equations_element) -> bool:
        for bool_condition in and_condition.conjunction_list:
            if not self._evaluate_boolcondition_on_tuple(bool_condition, parity_element, equations_element):
                return False
        return True

    def _evaluate_orcondition_on_tuple(self, or_condition: ORCondition, parity_element, equations_element) -> bool:
        print(f"\nEvalutaing {or_condition} on {parity_element} and {equations_element}")
        set_of_equations = equations_element.equations_set # type: ignore
        solution_without_sigma = solve_linear_equations(self.variables, set_of_equations, [])[0]
        print(f"Solution for equations is given by: {solution_without_sigma}.")

        for and_condition in or_condition.disjunction_list:
            if self._evaluate_andcondition_on_tuple(and_condition, parity_element, equations_element):
                return True
        return False


    def execute_command_from_abstract_state(self, current_state, command: Command):
        assert isinstance(current_state, self.lattice_class)
        command_type: CommandType = command.command_type
        current_set = current_state.tuples_set  # type: ignore
        new_set: Set[Tuple[self.tuple_class, self.summation_lattice]] = set() # type: ignore

        if command_type != CommandType.C_Assert:
            all_possible_equations_sets: List[self.summation_lattice] = list({t[1] for t in current_set}) # type: ignore
            all_possible_equations_outcome = \
                [self.summation_analyzer.execute_command_from_abstract_state(summation_element, command)
                 for summation_element in all_possible_equations_sets] # type: ignore
            for (parity_element, equations_element) in current_set:
                parity_cartesians_outcome: set = self.parity_analyzer.execute_command_on_carteisan(parity_element, command)
                equactions_outcome = all_possible_equations_outcome[all_possible_equations_sets.index(equations_element)]
                new_set.update({(parity, equactions_outcome) for parity in parity_cartesians_outcome})

        if command_type == CommandType.C_Assert:
            or_condition: ORCondition = command.command_parameters['ORC']
            succes = True
            for (parity_element, equations_element) in current_set:
                if not self._evaluate_orcondition_on_tuple(or_condition, parity_element, equations_element):
                    print(f"Assertion {or_condition} FAILED on <{parity_element}, {equations_element}>")
                    succes = False
            if succes:
                print("\nAssertin succeded!!!")
            
            new_set = current_state.tuples_set.copy() # type: ignore

        return self.lattice_class(parity_equations_tuples_set = new_set) # type: ignore

