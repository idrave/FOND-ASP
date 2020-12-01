from fondpddl.ctype import ConstType
from fondpddl.constant import Constant, TypedObject
from fondpddl.argument import Argument, ActionParam
from fondpddl.predicates import Predicate
from fondpddl.action import Action, GroundAction
from fondpddl.state import State
from fondpddl.domain import Domain
from fondpddl.problem import Problem
import fondpddl.algorithm
import fondpddl.encoding

def load_domain_and_problem(domain_file, problem_file):
    domain = Domain.parse(domain_file)
    problem = Problem.parse(problem_file, {domain.name : domain})
    return problem

def encode_clingo_problem(domain_file, problem_file, iterator=None,
                          expand_goal=False, log=False, logdict=None):
    iterator = iterator if iterator != None else fondpddl.algorithm.BreadthFirstSearch()
    problem = load_domain_and_problem(domain_file, problem_file)
    if log:
        print(str(problem.domain))
        print(str(problem))
    symbols = fondpddl.encoding.clingo_problem_encoding(
                problem, iterator, expand_goal=expand_goal, log=log, logdict=logdict)
    return symbols
