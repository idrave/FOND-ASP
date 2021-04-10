# FOND-ASP: FOND+ via ASP

This repo contains the FOND-ASP planner reported in:

* Ivan D. Rodriguez, Blai Bonet, Sebastian Sardiña, Hector Geffner: Flexible FOND Planning with Explicit Fairness Assumptions. ICAPS 2021 and [CoRR abs/2103.08391](https://arxiv.org/abs/2103.08391).

The FOND-ASP planning system is able is able to solve FOND+ planning problems: FOND problems with explicit conditional fairness conditions. This includes dual FOND problems (fair and unfair actions) and QNP, all integrated.

The FOND-ASP is written in Answer Set Programming (ASP) using [ASP Clingo system](https://potassco.org/).

- [FOND-ASP: FOND+ via ASP](#fond-asp-fond-via-asp)
  - [Setup](#setup)
    - [Using a Python Pipenv environment](#using-a-python-pipenv-environment)
  - [PDDL specification of FOND+ problems](#pddl-specification-of-fond-problems)
  - [Running the FOND-ASP planning system](#running-the-fond-asp-planning-system)
    - [Specialized solvers for standard FOND planning](#specialized-solvers-for-standard-fond-planning)
    - [Running against an ASP encoding](#running-against-an-asp-encoding)
  - [Running the experiments](#running-the-experiments)

## Setup

To run the system, you will need to have Clingo installed. In [Potassco](https://potassco.org/clingo/) webpage you can find information about how to set it up. The recommended installation is through a Conda environment running:

```bash
conda install -c potassco clingo
```

Independently of the setup method used, you should be able to run from command line:

```bash
clingo -h
```

Having Clingo installed, you will need to run:

```shell
git clone https://github.com/idrave/fond-asp.git
cd fond-asp
pip install -r requirements.txt
pip install -e .  # install project under `src/fcfondplanner`
```

### Using a Python Pipenv environment

You might want to apply the above steps inside an independent python environment. Here is one way using [Pipenv](https://pypi.org/project/pipenv/).

First install Clingo, by compiling and installing it via `CMAKE` as per instructions.

Next, install `FOND-ASP` and setup a Python environment:

```bash
$ git clone git@github.com:idrave/FOND-ASP.git
$ pipenv shell  // create a new environment
(fond-asp) $
```

Pipenv would have created a new environment, here named "`fond-asp`".

Next, install in the environment the dependencies stored in `Pipfile`:

```bash
$ pipenv install
```

Note that `Pipfile` makes reference to the `fond-asp` repo via the `git@` protocol, so we require ssh authentication to GitHub for this to work (so that Pipenv will be able to bring the dependency from the repo).

After this, all the dependencies would have been downloaded and stored them under a folder like `~/.local/share/virtualenvs/aspplanner-HxHD4kSc`

There is one more thing that needs to be installed: the Python Clingo component into the recently created Pipenv environment. When Clingo was installed, its  Python component where installed under the users' path `~/.local/lib/python3.8/site-packages/`. This include a `clingo.cpython-38-x86_64-linux-gnu.so` file and `clingo/` folder; copy them both to your Pipenv environment:

```bash
$ cp -a ~/.local/lib/python3.8/site-packages/clingo  ~/.local/share/virtualenvs/fond-asp.git-HxHD4kSc/lib/python3.8/site-packages/
```

Now `clingo` is part of the Pipenv environment, and all is ready to run.

## PDDL specification of FOND+ problems

The planning system uses the usual PDDL format for domain and problem specification. However, the PDDL is extended to allow the specification of  conditional fairness.

A fairness expression allow to define PDDL problems with _custom_ fairness assumptions for the FOND-ASP planner and has the form:

```pddl
((:fairness :a ...  :b ...)
```

where the ground actions following ```:a``` and ```:b``` represent the sets of actions A and B, respectively, describing a FOND+ constraint `[A, B]`: if any action in `A` is applied infinitely often in a state, all its effects will ensue infinitely often along that state, provided all the actions in `B` are executed _finitely_ often.

For example:

```pddl
(:fairness
        :a (go-right up) (go-right center) (go-right down)
        :b (go-left up) (go-left center) (go-left down)))
```

Note that the fairness constraints should mention only _ground_ actions. So, when operators have arguments, the relevant grounded instances must be listed in the fairness constraints. For example:

```pddl
 (:fairness
        :a (go-right p1) (go-right p2) (go-right p3)
        :b (go-left p1) (go-left p2) (go-left p3)))
```

which is equivalent to:

```pddl
 (:fairness
        :a (go-right p1) (go-right p2) (go-right p3)
        :b (go-left p1) (go-left p2) (go-left p3)))
 (:fairness
        :a (go-right p2)
        :b (go-left p1) (go-left p2) (go-left p3)))
 (:fairness
        :a (go-right p3)
        :b (go-left p1) (go-left p2) (go-left p3)))
```

To specify fairness constraints where `B` is empty, the `:b` section is fully omitted:

```pddl
(:fairness
        :a (go-up down p3 p2)
           (go-up p3 p2 p1)
           (go-up p2 p1 up)
           (go-down up p1 p2)
           (go-down p1 p2 p3)
           (go-down p2 p3 down))
```

## Running the FOND-ASP planning system

To see all options available run:

```bash
$ python -m fcfond.main -h
```

The most common way to use the planner is by running it over input PDDL files as follows:

```shell
$ python -m fcfond.main -pddl DOMAIN PROBLEM
```

where `DOMAIN` and `PROBLEM` are the PDDL files encoding the planning domain and problem to be solved.

For example:

```shell
$ python -m fcfond.main -pddl fcfond/domains/pddl/fond-sat/doors/domain.pddl fcfond/domains/pddl/fond-sat/doors/p01.pddl
```

This will use the default FOND+ solver implemented in `fcfond/planner_clingo/fondplus.lp` and leave the results in the default `output/` folder:

* `proc_p01.lp`: the full planning problem encoded as a set of ASP facts; see below for atoms used.
* `stdout.txt`: the standard output of the ASP solver, which shows a successful policy, if any has been found, via atoms `policy(S, A)` specifying the action `A` to be applied in state `S`.
* `metrics.csv`: the statistic of the solving task (e.g., time, no of models, etc.). 

To change the default output folder, use `-out` option.

The system can also be run with _specialized_ or _alternative_ solvers (via option `--planner`) and/or against domain encodings directly in ASP rather than PDDL (via option `--clingo`).

By default, the system uses the FOND+ solver `fcfond/planner_clingo/fondplus.lp`. However, one can (build and) specify which solver to use via option `--planner`:

```shell
python -m fcfond.main DOMAIN PROBLEM -planner PLANNER
```

where `PLANNER` is the `.lp` file containing the Clingo planner to be used.

Two specialized solvers are provided for strong and strong-cyclic planning; [see below](#specialized-solvers-for-standard-fond-planning).

In general, an ASP solver would expect a problem specified via a set of facts using following atoms:

* `state(S)`: `S` is a state
* `initialState(S)`: `S` is the initial state
* `goal(S)`: `S` is a goal state
* `action(A)`: `A` is an action
* `transition(S1, A, S2)`: there is a transition from state `S1` to state `S2` applying action `A`
* `con_A(A, I)`: action `A` belongs to set of constraints `A_I`
* `con_B(A, I)`: action `A` belongs to set of constraints `B_I`

When the system receives PDDL files, the problem is first translated to an ASP encoding using the above atoms.

The **output of a solver** should be atoms `policy(S, A)` specifying the action `A` to be applied in state `S`. In our sample experiments, the states and actions are represented as integers. To make the output more human readable, one can include the following rule in our program:

```asp
#show policy(State, Action): policy(IdS, IdA), id(state(State), IdS), id(action(Action), IdA), reach(IdS).
```

Where `id/2` symbols are generating automatically by the PDDL parser to describe the states and actions assigned to each integer ID.

### Specialized solvers for standard FOND planning

Two _specialized_ planners are provided to solve _standard_ (i.e., non-dual) FOND planning problems:

* `fcfond/planner_clingo/specialized/planner_strong.lp`: this is a conditional planner using adversarial semantics under which solutions are strong plans. It can be used via option `--strong`.
* `fcfond/planner_clingo/specialized/planner_strongcyclic.lp`: this is a strong-cyclic planner using state-fair semantics under which solutions are strong-cyclic plans. It can be used via option `--strongcyclic`.

The benchmark from the FOND-SAT planning system are included in this repo under [fcfond/domains/pddl/fond-sat/](fcfond/domains/pddl/fond-sat).

The two specializations for classical FOND planning can be used directly against the original PDDL domain and problem files, that is, the files with no `(:fairness )` statements.

To solve a FOND problem using the specialized planner for _**pure strong**_ planning (adversarial) semantics:

```shell
$ python -m fcfond.main -pddl DOMAIN PROBLEM --strong
```

which is equivalent to:

```shell
$ python -m fcfond.main -pddl DOMAIN PROBLEM --planner fcfond/planner_clingo/specialized/planner_strong.lp
```

For example:

```shell
$ python -m fcfond.main --strong -pddl fcfond/domains/pddl/fond-sat/doors/domain.pddl fcfond/domains/pddl/fond-sat/doors/p01.pddl
```

Similarly, to solve a FOND problem using the specialized planner for _**pure strong-cyclic**_ planning (state-action fairness) semantics:

```shell
$ python -m fcfond.main -pddl DOMAIN PROBLEM --strongcyclic
```

which is equivalent to:

```shell
$ python -m fcfond.main -pddl DOMAIN PROBLEM --planner fcfond/planner_clingo/specialized/planner_strongcyclic.lp
```

For example:

```shell
$ python -m fcfond.main --strongcyclic -pddl fcfond/domains/pddl/fond-sat/beam-walk/domain.pddl fcfond/domains/pddl/fond-sat/beam-walk/p01.pddl
```

**NOTE:** Observe that we can solve standard FOND planning problems using the default FOND+ solver (`fcfond/planner_clingo/fondplus.lp`):

* For pure strong planning, one just uses the original PDDL files with no `(:fairness :a ... b: ...)` clauses so that every non-determinism is assumed of adversarial type.
* For pure strong-cyclic planning, one needs to extend the original PDDL domain file to include corresponding fairness constraints for each non-deterministic ground action `a` of the form `[A={a},B=empty]`. This means one `(:fairness :a GROUND_ACTION)` for each _ground_ action in the problem needs to be included.

### Running against an ASP encoding

While the above examples make use of PDDL specifications (as domain and problem `.pddl` files), it is also possible to directly specify a problem encoded via a collection of ASP facts (see above) above using option `--clingo`.

For example:

```shell
$ python -m fcfond.main -clingo fcfond/domains/clingo/clear.lp -out clear
['clingo', PosixPath('/home/ssardina/git/soft/planning/FOND/FOND-ASP.git/fcfond/planner_clingo/fondplus.lp'), 'fcfond/domains/clingo/clear.lp', '-n', '1', '-t', '1']
Status:  Finished
```

The results will be left in folder `clear/`.

**NOTE:** Since when given a PDDL encoding, the FOND-ASP system will translate it to an ASP encoding, one could use that encoding later on; for example:

```shell
python -m fcfond.main -clingo output/proc_p01.lp
```

Finally, at the extreme, one can directly use the Clingo solver to run a particular planner directly on a particular ASP encoding of a problem:

```shell
clingo PLANNER DOMAIN
```

In this case, no planner and no specific encoding provided in this repo will be used. For example:

```shell
$ python -m fcfond.main --strongcyclic  -pddl fcfond/domains/pddl/fond-sat/beam-walk/domain.pddl fcfond/domains/pddl/fond-sat/beam-walk/p01.pddl

$ clingo fcfond/planner_clingo/specialized/planner_strongcyclic.lp output/proc_p01.lp

clingo version 5.4.0
Reading from ...go/specialized/planner_strongcyclic.lp ...
Solving...
Answer: 1
policy("<next-fwd(p0,p1),next-fwd(p1,p2),next-fwd(p2,p3),next-bwd(p1,p0),next-bwd(p2,p1),next-bwd(p3,p2),ladder-at(p0),position(p0)>","climb(p0)") policy("<next-fwd(p0,p1),next-fwd(p1,p2),next-fwd(p2,p3),next-bwd(p1,p0),next-bwd(p2,p1),next-bwd(p3,p2),ladder-at(p0),position(p0),up()>","walk-on-beam(p0,p1)") policy("<next-fwd(p0,p1),next-fwd(p1,p2),next-fwd(p2,p3),next-bwd(p1,p0),next-bwd(p2,p1),next-bwd(p3,p2),ladder-at(p0),position(p1),up()>","walk-on-beam(p1,p2)") policy("<next-fwd(p0,p1),next-fwd(p1,p2),next-fwd(p2,p3),next-bwd(p1,p0),next-bwd(p2,p1),next-bwd(p3,p2),ladder-at(p0),position(p1)>","walk(p1,p0)") policy("<next-fwd(p0,p1),next-fwd(p1,p2),next-fwd(p2,p3),next-bwd(p1,p0),next-bwd(p2,p1),next-bwd(p3,p2),ladder-at(p0),position(p2),up()>","walk-on-beam(p2,p3)") policy("<next-fwd(p0,p1),next-fwd(p1,p2),next-fwd(p2,p3),next-bwd(p1,p0),next-bwd(p2,p1),next-bwd(p3,p2),ladder-at(p0),position(p2)>","walk(p2,p1)") policy("<next-fwd(p0,p1),next-fwd(p1,p2),next-fwd(p2,p3),next-bwd(p1,p0),next-bwd(p2,p1),next-bwd(p3,p2),ladder-at(p0),position(p3)>","walk(p3,p2)")
SATISFIABLE

Models       : 1+
Calls        : 1
Time         : 0.007s (Solving: 0.00s 1st Model: 0.00s Unsat: 0.00s)
CPU Time     : 0.007s
```
## Running the experiments

To run the built-in set of experiments using the `FOND-ASP` planner for FOND+ dual problems use:

```bash
python -m fcfond.main EXPERIMENTS -out OUTPUT
```

Where `EXPERIMENTS` is one or more available experiments for the planner. Some available experiments and sub-experiments (which can also be run independently) are:

- `qnp`
  - `clear_qnp`
  - `on_qnp`
  - `gripper_qnp`
  - `delivery_qnp`
- `ltl`
  - `list`
  - `double-list`
  - `tree`
  - `graph`
  - `minlist`
  - `member-tree`
  - `swamp`
- `foot`
  - `footXX`, for an odd `XX` from `03` to `21`
- `sequential`
- `sequential`
- `sequential`
  - `sequentialXX`, for `XX` from `02` to `10`
- `nested`
  - `nestedXX`, for `XX` from `02` to `10`
- `unfair_qnp`: QNPs without terminating solution
- `fond_sat`: several domains of pure strong and pure strong cyclic planning

To get a list of more available experiments type

```bash
$ python -m fcfond.main -list [LIST]
```

Where `LIST` can be one of the experiment lists above.

The results will be left under folder `OUTPUT` and will include:

* `stdout.txt`: file containing the standard output given by Clingo solver when run over the domains. This shows the resulting policy, among other types of information.
* `metrics.csv`: contains a summary of several performance metrics
* `.lp` files with Clingo symbols corresponding to the input domains