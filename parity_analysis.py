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
        
    def all_elements():
        return [PL.Top,PL.Bottom,PL.Odd,PL.Even]
        

def create_cartesian_product_lattice(variables, lattice_class):
    #This function creates the cartesian product of n copies of the lattice, one of each variable

    class cartesian_prodcut:
        def __init__(self, tuple):
            self.tuple = tuple
            self.index_of_variables = {v: i for i, v in enumerate(variables)}

        def top():
            return cartesian_prodcut(tuple(lattice_class.top() for _ in variables))
        
        def bottom():
            return cartesian_prodcut(tuple(lattice_class.bottom() for _ in variables))
        
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
            return cartesian_prodcut(meet_tuple)

        def join(el1,el2):
            join_tuple = ()
            for v in variables:
                new_pl_el = lattice_class.join([el1[v], el2[v]])
                join_tuple = join_tuple + (new_pl_el,)
            return cartesian_prodcut(join_tuple)

        def __repr__(self) -> str:
            return self.tuple.__repr__()
        
        def __copy__(self):
            copy_of_tuple = tuple(value for value in self.tuple)
            return cartesian_prodcut(copy_of_tuple)
        
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
            return [cartesian_prodcut(tup) for tup in res]
    
    return cartesian_prodcut

def create_disjunctive_completion_lattice(lattice_class):
    #This function creates the disjunctive completion of a lattice
    class disjunctive_completion:
        def __init__(self, set):
            self.set: set=set #elements is a set of class objects from the lattice_class

        def top():
            return disjunctive_completion(set(lattice_class.all_elements())) 

        def bottom():
            return disjunctive_completion(set())
        
        def leq(el1,el2):
            return el1.set.issubset(el2.set)
        
        def meet(el1,el2):
            return el1.set.intersection(el2.set)
        
        def join(el1,el2):
            return el1.set.union(el2.set)
        
        def __repr__(self) -> str:
            return self.set.__repr__()
        
        def __copy__(self):
            return disjunctive_completion({s.__copy__() for s in self.set})
        
        def all_elements():
            res = [set()] 
            base_lattice_all = lattice_class.all_elements()
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

def example():
    pl_cp_class = create_cartesian_product_lattice(['x','y'], PL)
    print(pl_cp_class.top())
    el1 = pl_cp_class((PL.Top,PL.Bottom))
    el2 = pl_cp_class((PL.Even,PL.Bottom))
    print(el1.meet(el2))
    print(len(pl_cp_class.all_elements()))

    pl_rp_class = create_relational_product_lattice(['x','y'],PL)
    top = pl_rp_class.top()
    bottom = pl_rp_class.bottom()
    print(top.meet(bottom))
    print(top.join(bottom))
    print(bottom.leq(top))

# example()