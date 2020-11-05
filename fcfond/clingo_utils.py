import clingo
import sys

def extract_symbols(load, ground: list):
    ctl = clingo.Control()
    ctl.load(load)
    ctl.ground(ground)
    with ctl.solve(yield_=True) as handle:
        if handle.get().satisfiable:
            symbols = next(handle).symbols(shown=True)
        else:
            symbols = None
    return symbols

def replace_symbols(load, ground, name, arity, rules_replace):
    ctl = clingo.Control()
    ctl.load(load)
    ctl.ground(ground)
    ctl.solve()
    ctl.cleanup()
    with ctl.backend() as bck:
        assert isinstance(bck, clingo.Backend)
        for i, sym_atom in enumerate(ctl.symbolic_atoms.by_signature(name, arity)):
            atom = bck.add_atom(clingo.Function('id', [sym_atom.symbol, i]))
            bck.add_rule([atom])
    ctl.cleanup()
    ctl.add('base', [], rules_replace)
    ctl.ground([('base', [])])
    with ctl.solve(yield_=True) as handle:
        try:
            symbols = next(handle).symbols(shown=True)
        except:
            symbols = None #Unsat
    return symbols
        