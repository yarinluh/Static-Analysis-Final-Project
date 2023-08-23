from saav_parser import Program
from control_flow_graph import ControlFlowGraph
from fixpoint import vanilla_fixpoint, chaotic_iteration
from pathlib import Path
from abstract_state_parity import ParityStaticAnalyzer

def example1():
    path_to_program: Path = Path('.\examples\example1.txt')
    p = Program(path_to_program)

    cfg = ControlFlowGraph(program=p)

    parity_analyzer: ParityStaticAnalyzer = ParityStaticAnalyzer(variables=['n', 'i', 'j'])

    vanilla_fixpoint(cfg, parity_analyzer)
    chaotic_iteration(cfg, parity_analyzer)

def example2():
    path_to_program: Path = Path('.\examples\example2.txt')
    p = Program(path_to_program)

    cfg = ControlFlowGraph(program=p)

    parity_analyzer: ParityStaticAnalyzer = ParityStaticAnalyzer(variables=['n', 'i', 'j'])

    chaotic_iteration(cfg, parity_analyzer)

def example3():
    path_to_program: Path = Path('.\examples\example3.txt')
    p = Program(path_to_program)

    cfg = ControlFlowGraph(program=p)

    parity_analyzer: ParityStaticAnalyzer = ParityStaticAnalyzer(variables=['n', 'i', 'j'])

    chaotic_iteration(cfg, parity_analyzer)

def example4():
    path_to_program: Path = Path('.\examples\example4.txt')
    p = Program(path_to_program)

    cfg = ControlFlowGraph(program=p)

    parity_analyzer: ParityStaticAnalyzer = ParityStaticAnalyzer(variables=['n', 'm', 'i', 'j'])

    chaotic_iteration(cfg, parity_analyzer)

def example5():
    #This example highlights a bug in our current analysis that's leading to it not being sound
    path_to_program: Path = Path('.\examples\example5.txt')
    p = Program(path_to_program)

    cfg = ControlFlowGraph(program=p)

    parity_analyzer: ParityStaticAnalyzer = ParityStaticAnalyzer(variables=['n'])

    chaotic_iteration(cfg, parity_analyzer)

def example6():
    #This example highlights a bug in our current analysis that's leading to it not being sound
    path_to_program: Path = Path('.\examples\example6.txt')
    p = Program(path_to_program)

    cfg = ControlFlowGraph(program=p)

    parity_analyzer: ParityStaticAnalyzer = ParityStaticAnalyzer(variables=['n','m','i','j'])

    chaotic_iteration(cfg, parity_analyzer)


example6()