from fondpddl.ctype import ConstType
from fondpddl.constant import Constant, TypedObject
from fondpddl.argument import Argument, ActionParam
from fondpddl.predicates import Predicate
from fondpddl.domain import Domain
from fondpddl.problem import Problem
import fondpddl.algorithm
import fondpddl.encoding
import logging

logger = logging.getLogger(__name__)
LOG_SEPARATOR = "#"*20

def load_domain_and_problem(domain_file, problem_file) -> fondpddl.problem.Problem:
    """Builds a full planning Problem from PDDL domain and problem files

    Args:
        domain_file (str): path to PDDL domain file 
        problem_file (str): path to PDDL problem file 

    Returns:
        fondpddl.problem.Problem: a full planning Problem object
    """
    domain = Domain.parse(domain_file)
    problem = Problem.parse(problem_file, {domain.name : domain})
    return problem

def encode_clingo_problem(domain_file, problem_file, iterator=fondpddl.algorithm.BreadthFirstSearch(),
                          expand_goal=False, track=True, logdict=None, store_effect_changes=False):
    """Encode a PDDL domain and problem file into a ASP program in Clingo

    Args:
        domain_file (str): path to domain file
        problem_file (str): path to problem file
        iterator (fondpddl.algorithm, optional): algorithm to traverse TS. Defaults to None.
        expand_goal (bool, optional): goal states should be expanded when traversing TS. Defaults to False.
        track (bool, optional): [description]. Defaults to True.
        logdict (dict, optional): dictionary to store result info. Defaults to None.
        store_effect_changes (bool, optional): store the effect changes in actions. Defaults to False.

    Returns:
        [type]: [description]
    """
    problem = load_domain_and_problem(domain_file, problem_file)
    logger.debug(f"{LOG_SEPARATOR} DOMAIN {LOG_SEPARATOR}")
    logger.debug(str(problem.domain))
    logger.debug(f"{LOG_SEPARATOR} PROBLEM {LOG_SEPARATOR}")
    logger.debug(str(problem))
    symbols = fondpddl.encoding.clingo_problem_encoding(
                problem, iterator, expand_goal=expand_goal, track=track, logdict=logdict, store_effect_changes=store_effect_changes)
    return symbols

def get_labeled_graph(domain_file, problem_file, iterator=None,
                        expand_goal=True, track=True, logdict=None):
    iterator = iterator if iterator != None else fondpddl.algorithm.BreadthFirstSearch()
    problem = load_domain_and_problem(domain_file, problem_file)
    logger.debug(str(problem.domain))
    logger.debug(str(problem))
    symbols = fondpddl.encoding.clingo_problem_graph(
                problem, iterator, expand_goal=expand_goal, logdict=logdict)
    return symbols
