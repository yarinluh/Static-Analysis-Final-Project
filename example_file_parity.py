from saav_parser import Program
from control_flow_graph import ControlFlowGraph
from fixpoint import vanilla_fixpoint, chaotic_iteration
from pathlib import Path
from analysis_parity import ParityStaticAnalyzer

def run_parity_example(index: int):
    path_to_program: Path = Path(f'examples_pairty\example{index}.txt')
    p = Program(path_to_program)

    cfg = ControlFlowGraph(program=p)

    parity_analyzer: ParityStaticAnalyzer = ParityStaticAnalyzer(variables=p.program_variables)

    # vanilla_fixpoint(cfg, parity_analyzer)
    chaotic_iteration(cfg, parity_analyzer)

print("Started!")
run_parity_example(7)
