from control_flow_graph import ControlFlowGraph
from time import time

def vanilla_fixpoint(cfg, analyzer):
    nodes = cfg.nodes
    states_vector = [analyzer.lattice_class.bottom() for _ in nodes]
    start_node = cfg.find_start_label()
    states_vector[start_node] = analyzer.lattice_class.top()
    iteration = 0
    while True:
        print("iteration",iteration)
        new_vector = states_vector
        for node in nodes:
            new_vector = update_node_state(cfg,states_vector,node,analyzer)
        if new_vector == states_vector: 
            break
        else:
            states_vector = new_vector
        iteration = iteration + 1
    return states_vector

def chaotic_iteration(cfg, analyzer):
    nodes = cfg.nodes
    states_vector = [analyzer.lattice_class.bottom() for _ in nodes]
    start_node = cfg.find_start_label()
    states_vector[start_node] = analyzer.lattice_class.top()
    worklist = set(nodes)
    iteration = 0
    start_time = time()

    while worklist:
        print(f"\nIteration #{iteration} (started after {int(time()-start_time)} seconds).")
        print(f"Current worklist: {worklist}.")
        node = worklist.pop()
        new_vector = update_node_state(cfg, states_vector, node, analyzer)
        if new_vector != states_vector: 
            dependencies = create_dependencies_of_node(cfg,node)
            worklist=worklist.union(dependencies)
        states_vector = new_vector
        iteration = iteration + 1
    return states_vector
                
def update_node_state(cfg, states_vector, node, analyzer):
    new_vector = states_vector.copy()
    ingoing_edges = cfg.ingoing_edges(node)
    if ingoing_edges:
        ingoing_states = []
        for line in ingoing_edges:
            print("\n",line)
            start = line.start_label

            print("\n",start,states_vector[start])
            new_state = analyzer.execute_command_from_abstract_state(states_vector[start], line.command)
            
            print("\n",node,new_state)
            ingoing_states.append(new_state)
        new_state_for_node = analyzer.lattice_class.join_list(ingoing_states)
        if len(ingoing_edges) > 1:
            print("\n","join_result for",node,new_state_for_node)
        new_vector[node] = new_state_for_node
    return new_vector

def create_dependencies_of_node(cfg,node):
    result = set()
    outgoing_edges = cfg.outgoing_edges(node)
    for line in outgoing_edges:
        end = line.end_label
        result.add(end)
    return result
