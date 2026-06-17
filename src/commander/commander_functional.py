"""
TODO: command nesting
"""
from logging import warning
from dataclasses import dataclass
from collections.abc import Callable
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion
import re

type Action = Callable[[list[str]], None] #a command takes variables
type Command = tuple[int, Action] #a command takes variables

@dataclass
class ReturnCommanderFunctional():
    execute: Callable[[str], None]
    dict_command: dict[str, Command]


def commander_functional(dict_command: dict[str, Command], default_pack) -> ReturnCommanderFunctional:
    def list_commands(args: list[str]):
        print("available commands:")
        for command in dict_command:
            print(f"- {command}")
    
    dict_command = dict_command | {
        "list.commands" : (0, list_commands),
        "?" : (0, list_commands),
    }

    def execute(s:str):
        if s == "":
            return
        l = re.split(r'\s+', s.strip())
        cmd = l[0]
        if cmd not in dict_command:
            warning(f"command {cmd} not found")
            return
        n, f = dict_command[cmd]
        if n!= -1 and len(l) - 1 != n:
            warning(f"command {cmd} expects {n} arguments, but got {len(l) - 1}")
            return
        f(l[1:])
    return ReturnCommanderFunctional(execute=execute, dict_command=dict_command)

def get_completer(dict_command: dict[str, Command]):
    class CommandCompleter(Completer):
        def get_completions(self, document, complete_event):
            text = document.text
            for cmd in dict_command:
                if cmd.startswith(text):
                    yield Completion(
                        cmd[len(text):],
                        start_position=0,
                        display=f"{cmd} ({dict_command[cmd][0]} args)",
                    )
    completer = CommandCompleter()
    return completer

import subprocess
def shell(args: list[str]):
    if len(args) == 0:
        return
    subprocess.run(args)
default_pack = {
    "shell" : (-1, shell),
}

def commander_prompt_toolkit_loop(dict_command: dict[str, Command], default_pack = default_pack):
    dict_command = dict_command | default_pack
    commander_func = commander_functional(dict_command, default_pack = default_pack)
    session = PromptSession(completer=get_completer(commander_func.dict_command))
    while True:
        try:
            text = session.prompt()
            commander_func.execute(text)
        except KeyboardInterrupt:
            continue  # Ctrl-C pressed. Try again.
        except EOFError:
            break  # Ctrl-D pressed. Exit.
    print("Goodbye!")