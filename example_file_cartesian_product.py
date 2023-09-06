from pathlib import Path
from saav_parser import Program
from control_flow_graph import ControlFlowGraph
from cartesian_product_parity_summation import ParitySummationCartesianProduct
from fixpoint import chaotic_iteration

def run_example(index: int):
    path_to_program: Path = Path(f'combined_examples\example{index}.txt')
    p = Program(path_to_program)

    cfg = ControlFlowGraph(program=p)

    summation_analyser: ParitySummationCartesianProduct = \
        ParitySummationCartesianProduct(variables=p.program_variables,
                                        coefficiets_range=(-1, 1),
                                        integer_range=(-1, 1))

    # cfg.run_cfg()
    cfg.plot_graph()
    # vanilla_fixpoint(cfg, parity_analyzer)
    result = chaotic_iteration(cfg, summation_analyser)
    for item in result:
        print(item)


run_example(1)
