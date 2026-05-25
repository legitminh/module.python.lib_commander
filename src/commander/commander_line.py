from dataclasses import dataclass
from typing import Any, Callable, Dict, NamedTuple, Optional, Union, override
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion
from abc import ABC, abstractmethod
"""
A commander that executes commands line by line using prompt_toolkit. Useful for testing and debugging.
DEPRECATED
"""

def input_string() -> str:
    return input().rstrip()

def input_interable(sep: str = " ") -> list[str]:
    return input_string().split(sep)

def str_is_int(s: str) -> bool:
    try:
        int(s)
        return True
    except ValueError:
        return False


class Valiable(ABC):
    """
    validated variable of a string input
    """
    name: str
    description: str = ""
    @abstractmethod
    def validate(self, value: str) -> bool: pass

class ValiableMembership(Valiable):
    """
    validated variable of pure string
    """
    def __init__(self, club : list[str]):
        super().__init__()
        self.club = club

    @override
    def validate(self, value: str) -> bool:
        return value in self.club
    description: str = ""

# class ValiableString(Valiable):    
#     def __init__(self, name: str, validator: Callable[[str], bool] = lambda x: True, required: bool = True, description: str = "") -> None:
#         super().__init__(name, lambda x: x, validator, required, description)

class Command:
    name: str = ""
    params: list[Valiable] = []
    async def run(self, ctx, **kwargs):
        raise NotImplementedError

class SayHi(Command):
    name = "say_hi"
    async def run(self, ctx, **kwargs):
        return "hi"

class CommanderLine:
    """
    A simple command line interface framework that supports nested commands and functional parameters.
    To use, subclass and add commands to cmd_list in __init__ function, then call main() to start the interface.

    Inherit this class to use it
    """

    def __init__(self) -> None:
        self.commands = []
        self.validators : list[Valiable] = []
        
    def get_validator_command_name(self) -> Valiable:
        commands = self.commands
        class ValiableCommandName(ValiableMembership):
            def __init__(self):
                super().__init__(
                    [command.name for command in commands]
                )
        return ValiableCommandName()

    def output(self, l):
        print(l)

    def reset(self):
        self.validators = [self.get_validator_command_name()]

    def is_valid(self, token): return len(token.strip()) != 0

    def get_completer(self):
        commands = self.commands
        class CompleterCommander(Completer):
            def get_completions(self, document, complete_event): 
                text = document.text
                current_token = text.split()[-1]
                
                for command in commands:
                    if command.name.startswith(text):
                        yield Completion(
                            command.name,
                            start_position=-len(text),
                            display=command.name+" (command)",
                        )
        return CompleterCommander()

    def execute(self, command: Command, args: list[str]):
        ...

    def main(self):
        """
        main loop of the commander, keeps taking input until "end" command is executed
        """
        session = PromptSession(completer=self.get_completer())
        while True:
            try:
                text = session.prompt()
                print("You entered:", text)
            except KeyboardInterrupt:
                self.reset()
                continue  # Ctrl-C pressed. Try again.
            except EOFError:
                break  # Ctrl-D pressed. Exit.

if __name__ == "__main__":
    class CommanderLineTest(CommanderLine):
        def __init__(self) -> None:
            super().__init__()
            self.commands = [
                SayHi()
            ]
    test = CommanderLineTest()
    test.main()