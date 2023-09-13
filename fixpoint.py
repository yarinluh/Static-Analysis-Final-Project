from control_flow_graph import ControlFlowGraph
from time import time

def vanilla_fixpoint(cfg, analyzer):
    nodes = cfg.nodes
    states_dictionary = {n: analyzer.lattice_class.bottom() for n in nodes}
    start_node = cfg.find_start_label()
    states_dictionary[start_node] = analyzer.lattice_class.top()
    iteration = 0
    while True:
        print("iteration",iteration)
        new_dictionary = states_dictionary.copy()
        for node in nodes:
            new_dictionary = update_node_state(cfg,new_dictionary,node,analyzer)
        if new_dictionary == states_dictionary: 
            break
        else:
            states_dictionary = new_dictionary
        iteration = iteration + 1
    return states_dictionary

def chaotic_iteration(cfg, analyzer):
    nodes = cfg.nodes
    states_dictionary = {n: analyzer.lattice_class.bottom() for n in nodes}
    start_node = cfg.find_start_label()
    states_dictionary[start_node] = analyzer.lattice_class.top()
    worklist = set(nodes)
    iteration = 0
    start_time = time()

    while worklist:
        print(f"\nIteration #{iteration} (started after {int(time()-start_time)} seconds).")
        print(f"Current worklist: {worklist}.")
        node = worklist.pop()
        new_dictionary = update_node_state(cfg, states_dictionary, node, analyzer)
        if new_dictionary != states_dictionary: 
            dependencies = create_dependencies_of_node(cfg,node)
            worklist=worklist.union(dependencies)
        states_dictionary = new_dictionary
        iteration = iteration + 1
    return states_dictionary
                
def update_node_state(cfg, states_dictionary, node, analyzer):
    new_dictionary = states_dictionary.copy()
    ingoing_edges = cfg.ingoing_edges(node)
    if ingoing_edges:
        ingoing_states = []
        for line in ingoing_edges:
            print("\n",line)
            start = line.start_label

            print("\n",start,new_dictionary[start])
            new_state = analyzer.execute_command_from_abstract_state(states_dictionary[start], line.command)
            
            print("\n",node,new_state)
            ingoing_states.append(new_state)
        new_state_for_node = analyzer.lattice_class.join_list(ingoing_states)
        if len(ingoing_edges) > 1:
            print("\n","join_result for",node,new_state_for_node)
        new_dictionary[node] = new_state_for_node
    return new_dictionary

def create_dependencies_of_node(cfg,node):
    result = set()
    outgoing_edges = cfg.outgoing_edges(node)
    for line in outgoing_edges:
        end = line.end_label
        result.add(end)
    return result
