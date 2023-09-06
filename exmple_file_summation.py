from pathlib import Path
from saav_parser import Program
from control_flow_graph import ControlFlowGraph
from abstract_state_summation import SummationStaticAnalyzer
from fixpoint import chaotic_iteration

"""
Example 1 - This is the exmapmle from the paper.
Example 2 - Simple example to verify that (i + j) = (i + 1) + (j - 1).
Example 3 - Complicated example, tries to show that (i + m) + (x - m) = i + x. It does not work :(
Example 4 - Simple example to verify that if x = y and z = w than z + x = w + y.
Example 5 - Also fails :( because we only have x = y + n, and does not inclue relations like (n + m = i + j).
Example 6 - Works!
"""


def run_summation_example(index: int):
    path_to_program: Path = Path(f'examples_summation\example{index}.txt')
    p = Program(path_to_program)

    cfg = ControlFlowGraph(program=p)

    summation_analyser: SummationStaticAnalyzer = SummationStaticAnalyzer(variables=p.program_variables,
                                                                          maximal_absolute_value_of_integer=6)

    # cfg.run_cfg()
    # vanilla_fixpoint(cfg, parity_analyzer)
    chaotic_iteration(cfg, summation_analyser)


run_summation_example(5)