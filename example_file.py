
from saav_parser import Program
from control_flow_graph import ControlFlowGraph


p = Program('.\example_program.txt')
print(p)

cfg = ControlFlowGraph(program=p)
cfg.run_cfg()
cfg.plot_graph()
 