#script(python)
import re
import time
import clingo

def report_model(m):
    """
        Report model m

        @arg m : clingo.solving.Model (https://potassco.org/clingo/python-api/5.5/clingo/solving.html#clingo.solving.Model)
    """
    # print("type of model: ", type(m))
    # print("Model: ", m)
    # print(m.symbols(shown=True))

    # old way where we parsed the str rep of the model, not anymore, we use it as object!
    #plan = re.findall('plan\(state\((.+?)\),action\((.+?)\)\)', str(m))  # extract each (3, "DS")

    # extract set of rules from the plan/2 in the model returned as a clingo.solving.Model
    plan = []
    for f in m.symbols(shown=True): # extract function plan(State, Action)
        # now we access the plan/2 symbols to extract policy
        # https://potassco.org/clingo/python-api/5.5/clingo/symbol.html#clingo.symbol.Symbol
        if f.name == "plan":
            state = f.arguments[0]
            action = f.arguments[1]
            plan.append((state, action))

    print('#'*60)
    print(f'Solution {m.number} - Policy Size: {len(plan)} - Cost: {m.cost} - Optimal? {m.optimality_proven}')
    #print(str(m))
    print('='*60)

    # print out policy nicely with formatting
    #   number of rule :    state
    #                           action
    for i, rule in enumerate(plan):
        print(f"{i}: {rule[0]}\n\t {rule[1]}")
    print('#'*60, flush=True)
    pass

def model_to_string(m : clingo.solving.Model, shown=False):
    """Extract symbols of model as a list of strings

    https://potassco.org/clingo/python-api/5.5/clingo/solving.html#clingo.solving.Model
    https://potassco.org/clingo/python-api/5.5/clingo/symbol.html#clingo.symbol.Symbol
    """
    if shown:
        return sorted([str(f) for f in m.symbols(shown=True)])
    else:
        return sorted([str(f) for f in m.symbols(atoms=True)])

def main_one(prg):
    prg.configuration.solve.models = 1 # same as --models=n in cli (no of models)

    # combine the base program (problem to solve), with solver (FOND-ASP), with the small visualize to produce plan/2
    prg.ground([('base', []), ('fondplus', []), ('plan_show', [])])

    # solve it and call report_model(m) when a model is found
    prg.solve(on_model=report_model)


def main_one_alt(prg):
    """Multi-shot version: first solve, then ground plan/2"""
    prg.configuration.solve.models = 1 # same as --models=n in cli (no of models)

    # first combine the base program (problem to solve) with solver (FOND-ASP), and solve!
    prg.ground([('base', []), ('fondplus', []), ('plan_show', [])])
    prg.solve()

    # next, produce plan/2 interface
    prg.ground([('plan_show', [])])
    prg.solve(on_model=report_model)



def main_many(prg):
    prg.configuration.solve.models = 0 # same as --models=n in cli (no of models)

    # combine the base program (problem to solve), with solver (FOND-ASP), with the small visualize to produce plan/2
    prg.ground([('base', []), ('fondplus', []), ('plan_show', [])])

    # yield models one by one and collect them in solutions
    # https://potassco.org/clingo/python-api/5.5/clingo/solving.html#clingo.solving.SolveHandle
    solutions = []
    with prg.solve(yield_=True, on_model=report_model) as hnd:
        for m in hnd:
            # print(model_to_string(m))
            solutions.append(model_to_string(m))
            #print(hnd.get())    # get the result of the call (SAT/UNSAT)


    no_sol = len(solutions)
    print(f"Number of stable models found: {no_sol}")

    # there are at least 2 solution models, compare them!
    if no_sol > 1:
        sol1 = set(solutions[0])
        sol2 = set(solutions[1])

        print(f"Size of stable model 1: {len(sol1)}")
        print(f"Size of stable model 2: {len(sol2)}")

        print(f"Atoms in model 1 ONLY:\n\t {sol1.difference(sol2)}\n")
        print(f"Atoms in model 2 ONLY:\n\t {sol2.difference(sol1)}")

def main(prg):
    # just search for one model and that's it
    main_one(prg)

    # multi-shot version
    # main_one_alt(prg)

    # search for ALL the models: mostly for debugging
    # may take more even if 1 exists, as it tries to find (and fails)
    # to find a second one (check  Unsat time in in stats)
    # main_many(prg)

#end.
