from saav_parser import Program
from control_flow_graph import ControlFlowGraph
from fixpoint import vanilla_fixpoint
from parity_analysis import PL, create_relational_product_lattice

p = Program('.\example_program.txt')
#print(p)

cfg = ControlFlowGraph(program=p)
#cfg.run_cfg()
#cfg.plot_graph()

lattice = create_relational_product_lattice(['n', 'i', 'j'], PL)

vanilla_fixpoint(cfg, lattice)
#Currently doesn't work because of a bug in abstract state
