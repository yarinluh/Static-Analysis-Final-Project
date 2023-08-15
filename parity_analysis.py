from enum import Enum

class PL(Enum):
    #stands for Parity Lattice
    Top = 1
    Bottom = 2
    Odd = 3
    Even = 4

    def top():
        return PL.Top
    
    def bottom():
        return PL.Bottom
    
    def __le__(el1, el2):
        if el2 == PL.Top:
            return True
        if el1 == PL.Bottom:
            return True
        return el1 == el2
    
    def meet(el1,el2):
        if PL.leq(el1,el2):
            return el1
        if PL.leq(el2,el1):
            return el2
        else:
            return PL.Bottom
        
    def join(el1,el2):
        if PL.leq(el1,el2):
            return el2
        if PL.leq(el2,el1):
            return el1
        else:
            return PL.Top
        
    def join_list(el_list):
        curr_el = el_list[0]
        for i in range(1,len(el_list)):
            new_el = el_list[i]
            curr_el = PL.join(curr_el,new_el)   
        return curr_el
    
    def meet_list(el_list):
        curr_el = el_list[0]
        for i in range(1,len(el_list)):
            new_el = el_list[i]
            curr_el = PL.meet(curr_el,new_el)   
        return curr_el

    def all_elements():
        return [PL.Top,PL.Bottom,PL.Odd,PL.Even]
        
class P(Enum):
    Even = 0 
    Odd = 1
    
    def all_elements():
        return {P.Even,P.Odd}

def create_cartesian_product_lattice(variables,lattice_class):
    #This function creates the cartesian product of n copies of the lattice, one of each variable

    class cartesian_product:
        def __init__(self, tuple):
            self.tuple = tuple
            self.index_of_variables = {v: i for i, v in enumerate(variables)}

        def top():
            return cartesian_product(tuple(lattice_class.top() for _ in variables))
        
        def bottom():
            return cartesian_product(tuple(lattice_class.bottom() for _ in variables))
        
        def __getitem__(self, variable):
            index_of_variable = self.index_of_variables[variable]
            return self.tuple[index_of_variable]
        
        def __setitem__(self, variable_to_set, value):
            self.tuple = tuple(self[variable] if variable != variable_to_set else value
                               for variable in variables)
        
        def __eq__(self, other):
            return self.tuple == other.tuple

        def __hash__(self):
            return hash(self.tuple)

        def leq(el1,el2):
            #We assume they have the keys are the same in el1.mapping,el2.mapping
            return all([lattice_class.leq(el1[v], el2[v]) for v in variables])

        def meet(el1,el2):
            meet_tuple = ()
            for v in variables:
                new_pl_el = lattice_class.meet(el1[v], el2[v])
                meet_tuple = meet_tuple + (new_pl_el,)
            return cartesian_product(meet_tuple)

        def join(el1,el2):
            join_tuple = ()
            for v in variables:
                new_pl_el = lattice_class.join([el1[v], el2[v]])
                join_tuple = join_tuple + (new_pl_el,)
            return cartesian_product(join_tuple)
        
        def join_list(el_list):
            curr_el = el_list[0]
            for i in range(1,len(el_list)):
                new_el = el_list[i]
                curr_el = cartesian_product.join(curr_el,new_el)   
            return curr_el
        
        def meet_list(el_list):
            curr_el = el_list[0]
            for i in range(1,len(el_list)):
                new_el = el_list[i]
                curr_el = cartesian_product.meet(curr_el,new_el)   
            return curr_el

        def __repr__(self) -> str:
            return self.tuple.__repr__()
        
        def __copy__(self):
            copy_of_tuple = tuple(value for value in self.tuple)
            return cartesian_product(copy_of_tuple)
        
        def all_elements():
            res = [()]
            base_lattice_all = lattice_class.all_elements()
            for _ in variables:
                new_elements = [] 
                for cur_elem in res:
                    for base_elem in base_lattice_all:
                        new_elem = cur_elem + (base_elem,)
                        new_elements.append(new_elem)
                res = new_elements
            return [cartesian_product(tup) for tup in res]
    
    return cartesian_product

def create_disjunctive_completion_lattice(base_class):
    #This function creates the disjunctive completion of a lattice
    class disjunctive_completion:
        def __init__(self, set):
            self.set: set=set #elements is a set of class objects from the lattice_class

        def top():
            return disjunctive_completion(set(base_class.all_elements())) 

        def bottom():
            return disjunctive_completion(set())
        
        def leq(el1,el2):
            return el1.set.issubset(el2.set)
        
        def meet(el1,el2):
            return disjunctive_completion(el1.set.intersection(el2.set))
        
        def join(el1,el2):
            return disjunctive_completion(el1.set.union(el2.set))
        
        def join_list(el_list):
            curr_el = el_list[0]
            for i in range(1,len(el_list)):
                new_el = el_list[i]
                curr_el = disjunctive_completion.join(curr_el,new_el)   
            return curr_el
        
        def meet_list(el_list):
            curr_el = el_list[0]
            for i in range(1,len(el_list)):
                new_el = el_list[i]
                curr_el = disjunctive_completion.meet(curr_el,new_el)   
            return curr_el
        
        def __repr__(self) -> str:
            return self.set.__repr__()
        
        def __copy__(self):
            return disjunctive_completion({s.__copy__() for s in self.set})
        
        def all_elements():
            res = [set()] 
            base_lattice_all = base_class.all_elements()
            for base_elem in base_lattice_all:
                new_elements = []
                for cur_elem in res:
                    new_elements.append(cur_elem)
                    new_element = cur_elem.copy()
                    new_element.add(base_elem)
                    new_elements.append(new_element)
                res = new_elements
            return res            

    return disjunctive_completion            

def create_relational_product_lattice(variables,lattice_class):
    cartesian_product = create_cartesian_product_lattice(variables,lattice_class)
    relational_product = create_disjunctive_completion_lattice(cartesian_product)
    return relational_product

def create_tuple_class(variables,base_class):
    
    class tuple_class:
        def __init__(self,tuple):
            self.tuple = tuple
            self.index_of_variables = {v: i for i, v in enumerate(variables)}

        def __getitem__(self, variable):
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
        
        def __copy__(self):
            copy_of_tuple = tuple(value for value in self.tuple)
            return tuple_class(copy_of_tuple)
        
        def all_elements():
            res = [()]
            base_lattice_all = base_class.all_elements()
            for _ in variables:
                new_elements = [] 
                for cur_elem in res:
                    for base_elem in base_lattice_all:
                        new_elem = cur_elem + (base_elem,)
                        new_elements.append(new_elem)
                res = new_elements
            return [tuple_class(tup) for tup in res]

    return tuple_class

def create_tuple_subsets_lattice(variables,base_class):
    #this is like a relational product - only you don't need to start from a class
    tuple_class = create_tuple_class(variables,base_class)
    tuple_subsets_lattice = create_disjunctive_completion_lattice(tuple_class)
    return tuple_subsets_lattice

def example():
    variables = {'x','y','z'}

    lattice = create_tuple_subsets_lattice(variables,P)

    print(lattice.top())
    print(len(lattice.all_elements()))
    
example()
