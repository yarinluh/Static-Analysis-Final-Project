from typing import List
from pathlib import Path

from saav_parser.commands_part1 import Command

class ProgramLine:
    def __init__(self, line_text: str):
        splitted_line = line_text.split(' ')
        start_label = splitted_line[0]
        end_label = splitted_line[-1]
        if start_label[0] != "L" or not start_label[1:].isdigit() or \
             end_label[0] != "L" or not end_label[1:].isdigit():
            raise SyntaxError("Line does not start or ends with a labal!")
        self.start_label: int = int(start_label[1:])
        self.end_label: int = int(end_label[1:])

        command_text = line_text[len(start_label): -len(end_label)].strip()
        self.command: Command = Command(command_text)

    def __repr__(self) -> str:
        return f"L{self.start_label}   {self.command}   L{self.end_label}"


class Program:
    def __init__(self, program_file: Path):
        with open(program_file) as file:
            lines = [line.strip() for line in file]
            lines = [line for line in lines if line != ""]

        self.program_variables: List[str] = lines[0].split(' ')
        self.program_lines: List[ProgramLine] = [ProgramLine(line) for line in lines[1:]]

    def __repr__(self) -> str:
        s = ' '.join(self.program_variables) + "\n"
        for program_line in self.program_lines:
            s += f"\n{program_line}"
        return s
