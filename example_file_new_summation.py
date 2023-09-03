from pathlib import Path
from saav_parser import Program
from control_flow_graph import ControlFlowGraph
from new_summation_analysis import SummationStaticAnalyzer
from fixpoint import chaotic_iteration

def run_summation_example(index: int):
    path_to_program: Path = Path(f'examples_summation\example{index}.txt')
    p = Program(path_to_program)

    cfg = ControlFlowGraph(program=p)

    summation_analyser: SummationStaticAnalyzer = SummationStaticAnalyzer(variables=p.program_variables,
                                                                          coefficiets_range=(-1, 1),
                                                                          integer_range=(-4, 4))

    # cfg.run_cfg()
    # vanilla_fixpoint(cfg, parity_analyzer)
    chaotic_iteration(cfg, summation_analyser)


run_summation_example(5)