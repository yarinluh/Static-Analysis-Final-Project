from __future__ import annotations
from abc import abstractmethod, ABC
from enum import Enum
from typing import List, Type, Tuple, Dict, Set, Iterator
# from typing_extensions import Self

class Lattice(ABC):

    @abstractmethod
    def top() -> Lattice:
        pass

    @abstractmethod
    def bottom() -> Lattice:
        pass

    @abstractmethod
    def __eq__(self: Lattice, other: Lattice) -> bool:
        pass

    @abstractmethod
    def __le__(self: Lattice, other: Lattice) -> bool:
        pass

    @abstractmethod
    def meet(self: Lattice, other: Lattice) -> Lattice:
        pass

    @staticmethod
    def meet_list(element_list: List[Lattice]) -> Lattice:
        if len(element_list) == 0:  # Empty intersection == everything.
            return Lattice.top()
        meet_result: Lattice = element_list[0]
        for element in element_list:
            meet_result = meet_result.meet(element)
        return meet_result

    @abstractmethod
    def join(self: Lattice, other: Lattice) -> Lattice:
        pass

    @staticmethod
    def join_list(element_list: List[Lattice]) -> Lattice:
        if len(element_list) == 0:  # Empty union == nothing.
            return Lattice.bottom()
        join_result: Lattice = element_list[0]
        for element in element_list:
            join_result = join_result.join(element)
        return join_result

class Itemable(ABC):
    @abstractmethod
    def __getitem__(self, variable: str):
        pass
    @abstractmethod
    def __setitem__(self, variable: str, value):
        pass

class ItemableLattice(Itemable, Lattice):
    pass

def create_cartesian_product_lattice(variables: List[str], lattice_class: Type[Lattice]) -> Type[ItemableLattice]:
    #This function creates the cartesian product of n copies of the lattice, one of each variable

    class cartesian_product(ItemableLattice):
        def __init__(self, tuple: Tuple[lattice_class]):
            self.tuple: Tuple[lattice_class] = tuple
            self.index_of_variables: Dict[str, int] = {v: i for i, v in enumerate(variables)}

        @staticmethod
        def top() -> cartesian_product:
            return cartesian_product(tuple(lattice_class.top() for _ in variables))
        
        @staticmethod
        def bottom() -> cartesian_product:
            return cartesian_product(tuple(lattice_class.bottom() for _ in variables))
        
        def __eq__(self: cartesian_product, other: cartesian_product) -> bool:
            return self.tuple == other.tuple
        
        def __getitem__(self, variable: str) -> lattice_class:
            index_of_variable = self.index_of_variables[variable]
            return self.tuple[index_of_variable]
        
        def __setitem__(self, variable_to_set: str, value: lattice_class) -> None:
            self.tuple = tuple(self[variable] if variable != variable_to_set else value
                               for variable in variables)
        
        def __le__(self: cartesian_product, other: cartesian_product) -> bool:
            return all([self[var] <= other[var] for var in variables])
        

        def meet(self: cartesian_product, other: cartesian_product) -> cartesian_product:
            meet_tuple: Tuple[lattice_class] = tuple()
            for var in variables:
                new_element = self[var].meet(other[var])
                meet_tuple += (new_element, )
            return cartesian_product(tuple=meet_tuple)
        
        def join(self: cartesian_product, other: cartesian_product) -> cartesian_product:
            join_tuple: Tuple[lattice_class] = tuple()
            for var in variables:
                new_element = self[var].join(other[var])
                join_tuple += (new_element, )
            return cartesian_product(tuple=join_tuple)

        def __hash__(self):
            return hash(self.tuple)
        
        def __repr__(self) -> str:
            return self.tuple.__repr__()
        
        def __copy__(self):
            copy_of_tuple = tuple(value for value in self.tuple)
            return cartesian_product(copy_of_tuple)
    
    return cartesian_product

class Listable(ABC):
    """
    This is a lattice for which it is possible to count all elements in it.
    """
    @abstractmethod
    def all_elements() -> List[Listable]:
        pass
    
    @abstractmethod
    def copy(self: Listable) -> Listable:
        pass

class ListableLattice(Lattice, Listable):
    @abstractmethod
    def all_elements() -> List[ListableLattice]:
        pass
    
    @abstractmethod
    def copy(self: ListableLattice) -> ListableLattice:
        pass

    @abstractmethod
    def __iter__() -> Iterator[ListableLattice]:
        pass

def create_cartesian_product_listable_lattice(variables: List[str], lattice_class: Type[ListableLattice]) -> Type[ListableLattice]:
    cartesian_product_class: Type[Lattice] = create_cartesian_product_lattice(variables, lattice_class)

    class cartesian_product_listable(ListableLattice, cartesian_product_class):
        @staticmethod
        def all_elements() -> List[cartesian_product_listable]:
            result: List[Tuple[lattice_class]] = [tuple()]
            base_lattice_all: List[lattice_class] = lattice_class.all_elements()
            for _ in variables:
                new_elements = [] 
                for curent_element in result:
                    for base_element in base_lattice_all:
                        new_element = curent_element + (base_element, )
                        new_elements.append(new_element)
                result = new_elements
            return [cartesian_product_class(tup) for tup in result] # type: ignore
        
        def copy(self: cartesian_product_listable) -> cartesian_product_listable:
            tuple_copy = tuple(element.copy() for element in self.tuple) # type: ignore
            return cartesian_product_class(tuple_copy) # type: ignore

    return cartesian_product_listable

def create_disjunctive_completion_lattice(base_class: Type[Listable]) -> Type[ListableLattice]:
    #This function creates the disjunctive completion of a base class
    class disjunctive_completion(ListableLattice):
        def __init__(self, set: Set[base_class]):
            self.set: Set[base_class] = set #elements is a set of class objects from the lattice_class

        @staticmethod
        def top():
            return disjunctive_completion(set(base_class.all_elements())) 

        @staticmethod
        def bottom():
            return disjunctive_completion(set())
        
        def __eq__(self: disjunctive_completion, other: disjunctive_completion):
            return self.set == other.set
        
        def __le__(self: disjunctive_completion, other: disjunctive_completion):
            return self.set.issubset(other.set)
                
        def meet(self: disjunctive_completion, other: disjunctive_completion):
            return disjunctive_completion(set=self.set.intersection(other.set))
        
        def join(self: disjunctive_completion, other: disjunctive_completion):
            return disjunctive_completion(set=self.set.union(other.set))
        
        def __repr__(self) -> str:
            return self.set.__repr__()
        
        def copy(self: disjunctive_completion):
            return disjunctive_completion({s.copy() for s in self.set})
        
        def __iter__(self) -> Iterator[base_class]:
            for element in self.set:
                yield element
        
        @staticmethod
        def all_elements() -> List[disjunctive_completion]:
            result: List[Set[base_class]] = [set()] 
            base_lattice_all = base_class.all_elements()
            for base_elem in base_lattice_all:
                new_elements = []
                for cur_elem in result:
                    new_elements.append(cur_elem)
                    new_element = cur_elem.copy()
                    new_element.add(base_elem)
                    new_elements.append(new_element)
                result = new_elements
            return [disjunctive_completion(s) for s in result]            

    return disjunctive_completion            

def create_relational_product_lattice(variables: List[str], lattice_class: Type[ListableLattice]) -> Type[ListableLattice]:
    cartesian_product: Type[ListableLattice] = create_cartesian_product_listable_lattice(variables, lattice_class)
    relational_product: Type[ListableLattice] = create_disjunctive_completion_lattice(cartesian_product)
    return relational_product

class ListableItemable(Listable, Itemable):
    pass

def create_tuple_class(variables, base_class: Type[Listable]) -> Type[ListableItemable]:
    
    class tuple_class(ListableItemable):
        def __init__(self, tuple: Tuple[base_class]):
            self.tuple: Tuple[base_class] = tuple
            self.index_of_variables: Dict[str, int] = {v: i for i, v in enumerate(variables)}

        def __getitem__(self, variable) -> base_class:
            index_of_variable = self.index_of_variables[variable]
            return self.tuple[index_of_variable]
        
        def __setitem__(self, variable_to_set, value):
            self.tuple = tuple(self[variable] if variable != variable_to_set else value
                               for variable in variables)
        
        def __eq__(self, other):
            return self.tuple == other.tuple

        def __hash__(self):
            return hash(self.tuple)

        def __repr__(self) -> str:
            return self.tuple.__repr__()
        
        def copy(self):
            copy_of_tuple = tuple(value for value in self.tuple)
            return tuple_class(copy_of_tuple)
        
        @staticmethod
        def all_elements():
            result: List[Tuple[base_class]] = [tuple()]
            base_class_all = base_class.all_elements()
            for _ in variables:
                new_elements = [] 
                for curent_element in result:
                    for base_element in base_class_all:
                        new_element = curent_element + (base_element, )
                        new_elements.append(new_element)
                result = new_elements
            return [tuple_class(tup) for tup in result]

    return tuple_class

def create_tuple_subsets_lattice(variables: List[str], base_class: Type[Listable]) -> Type[ListableLattice]:
    #this is like a relational product - only you don't need to start from a class
    tuple_class: Type[ListableItemable] = create_tuple_class(variables, base_class)
    tuple_subsets_lattice: Type[ListableLattice] = create_disjunctive_completion_lattice(tuple_class)
    return tuple_subsets_lattice

class ListableEnum(type(Enum), type(Listable)):
    pass
