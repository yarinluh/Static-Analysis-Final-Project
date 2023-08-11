from saav_parser import Program, ProgramLine
from concrete_state import ConcreteState
from typing import List, Union
import networkx as nx
import matplotlib.pyplot as plt

def create_graph_from_program(program: Program) -> nx.DiGraph:
    G = nx.DiGraph()
    for program_line in program.program_lines:
        G.add_edge(*program_line.get_edge_label())
    return G

class ControlFlowGraph:
    def __init__(self, program: Program):
        self.program: Program = program
        self.nodes: List[int] = self.program.get_all_labels()
        
    def plot_graph(self):
        graph: nx.DiGraph = create_graph_from_program(self.program)
        pos = nx.spring_layout(graph)
        plt.figure()

        edge_labels: dict = {}
        for program_line in self.program.program_lines:
            edge_labels[program_line.get_edge_label] = str(program_line.command)

        nx.draw(graph, pos=pos, edge_color='black', width=1, linewidths=1, node_size=500, node_color='cyan',
                labels={node: node for node in graph.nodes()})
        
        nx.draw_networkx_edge_labels(graph, pos,
                                     edge_labels={program_line.get_edge_label(): str(program_line.command)
                                                  for program_line in self.program.program_lines},
                                                  font_size=16)

        plt.show()

    def ingoing_edges(self, node: int) -> List[ProgramLine]:
        return [program_line for program_line in self.program.program_lines
                if program_line.end_label == node]

    def outgoing_edges(self, node: int) -> List[ProgramLine]:
        return [program_line for program_line in self.program.program_lines
                if program_line.start_label == node]

    def find_start_label(self) -> int:
        for node in self.nodes:
            if len(self.ingoing_edges(node)) == 0:
                return node
        raise SyntaxError("Could not find a starting label!")

    def run_cfg(self):
        current_node: int = self.find_start_label()
        current_state: ConcreteState = ConcreteState()
        sucess: bool = True
        failed_assertion = False

        while True:
            outgoing_lines: List[ProgramLine] = self.outgoing_edges(current_node)
            if len(outgoing_lines) == 0:
                break
            
            possible_lines: List[ProgramLine] = [line for line in outgoing_lines
                                                 if current_state.is_possible_to_execute_command(line.command)]
            if len(possible_lines) == 0:
                # TODO ask Noam - can be assume that this is a syntax-failure?
                sucess = False
                break
            if len(possible_lines) >= 2:
                # TODO ask Noam - can be assume that this is a syntax-failure?
                sucess = False
                break

            line_to_take: ProgramLine = possible_lines[0]
            print(f"Performing {line_to_take} \n\ton state: {current_state}\n")

            next_state: Union[None, current_state] = current_state.execute_command_from_concrete_state(line_to_take.command)
            if next_state is None:
                failed_assertion = True
                break
            
            current_node = line_to_take.end_label
            current_state = next_state

        if not sucess:
            print(f"Running FAILED!\nTried to advance from L{current_node} when the state is: {current_state}")
            if len(possible_lines) == 0:
                print("but there was no way to do so.")
            else:  # len(possible_linse) >= 2
                print("but there was more than one way to do so.")
        elif failed_assertion:
            print(f"The assertion {line_to_take.command} was failed on state: {current_state}.")
        else:
            print(f"SUCESS! Reached an ending line with the state: {current_state}.")
        
