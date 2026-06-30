"""
TODO: command nesting
"""
from logging import warning
from dataclasses import dataclass
from collections.abc import Callable
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion
import re

MANUAL = \
"""
__THIS IS THE MANUAL__
type ? for list of commands. 
hit enter to run commands, each command is a line consisting of [command names] followed by arguments (separated by spaces).
wrap string arguments in \" characters
__END__

"""

type Action = Callable[[list[str]], None] #a command takes variables
type Command = tuple[int, Action] #a command takes variables

@dataclass
class ReturnCommanderFunctional():
    execute: Callable[[str], None]
    dict_command: dict[str, Command]

def get_l(s: str) -> list[str]:
    l = []
    cur_token = ""
    is_skip = False
    is_big_skip = False
    for i in s:
        if is_big_skip:
            if is_skip:
                cur_token += i
                is_skip = False
            elif i == "\\":
                is_skip = True
            elif i == "\"":
                is_big_skip = False
            else:
                cur_token += i
        elif is_skip:
            cur_token += i
            is_skip = False
        elif i == "\\":
            is_skip = True
        elif i == "\"":
            is_big_skip = True
        elif i == " ":
            if cur_token:
                l.append(cur_token)
                cur_token = ""
        else:
            cur_token += i
    l.append(cur_token)
    print(s,l)
    return l

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
        l = get_l(s)
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
    "open.manual": (0, lambda l: 
        print(MANUAL)
    )
}

def commander_prompt_toolkit_loop(dict_command: dict[str, Command], on_interrupt = None, on_quit = None, default_pack = default_pack):
    dict_command = dict_command | default_pack
    commander_func = commander_functional(dict_command, default_pack = default_pack)
    session = PromptSession(completer=get_completer(commander_func.dict_command))
    while True:
        try:
            text = session.prompt()
            commander_func.execute(text)
        except KeyboardInterrupt:
            if on_interrupt:
                on_interrupt()
            continue  # Ctrl-C pressed. Try again.
        except EOFError:
            break  # Ctrl-D pressed. Exit.
        finally:
            if on_quit:
                on_quit()
    print("Goodbye!")