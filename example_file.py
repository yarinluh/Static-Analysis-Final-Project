
from saav_parser import Program
from control_flow_graph import ControlFlowGraph


p = Program('.\example_program.txt')
print(p)

cfg = ControlFlowGraph(program=p)
print(cfg.find_start_label())
cfg.run_cfg()
