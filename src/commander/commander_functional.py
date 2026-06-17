"""
TODO: command nesting
"""
from logging import warning
from typing import Any, NamedTuple
from collections.abc import Callable
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion
import re

type Action = Callable[[list[str]], None] #a command takes variables
type Command = tuple[int, Action] #a command takes variables
type ReturnCommanderFunctional = Callable[[str], None]

def commander_functional(dict_command: dict[str, Command], ) -> ReturnCommanderFunctional:
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
    return execute

def get_completer(dict_command: dict[str, Command]):
    class CommandCompleter(Completer):
        def get_completions(self, document, complete_event):
            text = document.text
            for cmd in dict_command:
                if cmd.startswith(text):
                    yield Completion(
                        cmd[len(text):],
                        start_position=0,
                        display=f"{cmd} (command)",
                    )
    completer = CommandCompleter()
    return completer

def commander_prompt_toolkit_loop(dict_command: dict[str, Command]):
    commander_func = commander_functional(dict_command)
    session = PromptSession(completer=get_completer(dict_command))
    while True:
        try:
            text = session.prompt()
            commander_func(text)
        except KeyboardInterrupt:
            continue  # Ctrl-C pressed. Try again.
        except EOFError:
            break  # Ctrl-D pressed. Exit.
    print("Goodbye!")