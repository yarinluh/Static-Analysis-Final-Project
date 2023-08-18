from saav_parser import Program
from control_flow_graph import ControlFlowGraph
from fixpoint import vanilla_fixpoint, chaotic_iteration
from pathlib import Path
from abstract_state_parity import ParityStaticAnalyzer

path_to_program: Path = Path('.\example_program.txt')
p = Program(path_to_program)
#print(p)

cfg = ControlFlowGraph(program=p)
#cfg.run_cfg()
#cfg.plot_graph()

parity_analyzer: ParityStaticAnalyzer = ParityStaticAnalyzer(variables=['n', 'i', 'j'])

# vanilla_fixpoint(cfg, parity_analyzer)
chaotic_iteration(cfg, parity_analyzer)
#Currently doesn't work because of a bug in abstract state
