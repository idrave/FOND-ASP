import clingo
import sys

def extract_symbols(load: list, ground: list):
    ctl = clingo.Control()
    ctl.load(load)
    ctl.ground(ground)
    with ctl.solve(yield_=True) as handle:
        if handle.get().satisfiable:
            symbols = next(handle).symbols(shown=True)
        else:
            symbols = None
    return symbols
