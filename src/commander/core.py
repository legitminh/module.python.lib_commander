from typing import Any, Callable, Dict, Union
"""
A simple command line interface framework that supports nested commands and functional parameters.
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

CommandState = Union[Dict[str, tuple[int, Callable[..., Any]]],
                      tuple[int, Callable[..., Any]]]

class Commander:
    """
    A simple command line interface framework that supports nested commands and functional parameters.
    To use, subclass and add commands to cmd_list in __init__ function, then call main() to start the interface.
    """

    def __init__(self, cmd_list: Dict[str, tuple[int, Callable[..., Any]]] = {}):
        def repeat(l) -> None:
            self.output("repeating...", self.previous_exec[0], *self.previous_exec[1])
            self.execute(self.previous_exec[0], *self.previous_exec[1])

        def end(l) -> None:
            self.output("Terminated")
            self.is_running = False

        self.exec_no_record = set()  # commands that aren't recorded when executed
        self.exec_no_record.add(repeat)
        self.cmd_list = cmd_list
        self.cmd_list["end"] = (0, end)
        self.cmd_list["repeat"] = (0, repeat)
        self.state: CommandState = self.cmd_list
        self.previous_exec: tuple[Callable[..., Any], tuple[Any, ...]] = (lambda: None, ())
        self.is_running = True
        self.params: list[str] = []

    def execute(self, f: Callable[..., Any], *params: Any) -> None:
        # self.output(f, *params)
        if f not in self.exec_no_record:
            self.previous_exec = (f, params)
        f(*params)

    def output(self, *l):
        print(">>",*l)

    def reset_state(self):
        self.state = self.cmd_list
        self.params = []

    def is_valid(self, token): return len(token.strip()) != 0

    def input_token(self, token):
        """
        handles the input token, change state and execute commands accordingly
        """
        def confusion(previous_state, candidates):
            def resolution(l):
                if str_is_int(l[0]):
                    return previous_state[candidates[int(l[0])]]
                raise TypeError
                # return previous_state[l[0]]
            return resolution
        
        #read sequence
        if isinstance(self.state, tuple):
            #if is in functional parameter state
            if self.state[0] >= 0:
                self.state = (self.state[0] - 1, self.state[1])
                self.params.append(token)
        else:
            #if in function selection state
            if token in self.state:
                self.state = self.state[token]
            else:
                #recommend options
                candidates = []
                
                for i, key in enumerate(self.state.keys()):
                    if key.startswith(token):
                        candidates.append(key)
                lc = len(candidates)
                if lc == 0:
                    self.output("no valid command, options:", self.state.keys())
                elif lc == 1:
                    self.output("autocompleting option:",candidates[0])
                    self.state = self.state[candidates[0]]
                else:
                    for i, v in enumerate(candidates):
                        self.output(i, v)
                    self.output("options available, choose with int: ")
                    self.state = (1, confusion(self.state, candidates))
                
        
        #function execution sequence
        if isinstance(self.state, tuple):
            if self.state[0] == 0:
                self.execute(self.state[1], self.params)
                self.reset_state()

    def main(self):
        """
        main loop of the commander, keeps taking input until "end" command is executed
        """
        self.reset_state()
        while self.is_running:
            for token in input_interable():
                if self.is_valid(token):
                    self.input_token(token)