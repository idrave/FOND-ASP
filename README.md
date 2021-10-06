# FOND-ASP: FOND+ via ASP

This repo contains the FOND-ASP planner reported in:

* Ivan D. Rodriguez, Blai Bonet, Sebastian Sardiña, Hector Geffner: Flexible FOND Planning with Explicit Fairness Assumptions. ICAPS 2021 and [CoRR abs/2103.08391](https://arxiv.org/abs/2103.08391).

The FOND-ASP planning system is able is able to solve FOND+ planning problems: FOND problems with explicit conditional fairness conditions. This includes dual FOND problems (fair and unfair actions) and QNP, all integrated.

The FOND-ASP is written in Answer Set Programming (ASP) using [ASP Clingo system](https://potassco.org/).

- [FOND-ASP: FOND+ via ASP](#fond-asp-fond-via-asp)
  - [Setup](#setup)
    - [Using a Python Pipenv environment](#using-a-python-pipenv-environment)
  - [PDDL and ASP specifications of FOND+ problems](#pddl-and-asp-specifications-of-fond-problems)
    - [PDDL specifications](#pddl-specifications)
    - [ASP Encoding](#asp-encoding)
  - [Running FOND-ASP](#running-fond-asp)
  - [Panners/Solvers available](#pannerssolvers-available)
    - [Pure Strong under adversarial semantics](#pure-strong-under-adversarial-semantics)
    - [Pure Strong-cyclic under state-fair semantics](#pure-strong-cyclic-under-state-fair-semantics)
    - [Dual FOND: mix of adversarial and fair actions](#dual-fond-mix-of-adversarial-and-fair-actions)
  - [Running against an ASP encoding](#running-against-an-asp-encoding)
  - [Running the experiments](#running-the-experiments)

## Setup

To run the system, you will need to have Clingo installed. In [Potassco](https://potassco.org/clingo/) webpage you can find information about how to set it up. The recommended installation is through a Conda environment running:

```bash
$ conda install -c potassco clingo
```

Independently of the setup method used, you should be able to run from command line:

```bash
$ clingo -h
```

Having Clingo installed, you can get and setup FOND-ASP as follows:

```shell
$ git clone https://github.com/idrave/fond-asp.git
$ cd fond-asp
$ pip install -r requirements.txt
```

Finally, install the planner as an [editable project](https://packaging.python.org/guides/distributing-packages-using-setuptools/#working-in-development-mode):

```shell
$ pip install -e .  # install as editable project as per setup.py
```

Effectively this adds the folder to [`sys.path`](https://www.devdungeon.com/content/python-import-syspath-and-pythonpath-tutorial#toc-12) variable which is used by Python to search for modules. This means you can now use/run the planner from anywhere, as it is installed as a packge, and any change in the source of the planner will be seen automatically.

For example:

```shell
$ python -m fcfond.main -h
usage: main.py [-h] [-list [LIST]] [-pddl PDDL [PDDL ...]] [-clingo CLINGO [CLINGO ...]] [-out OUT] [-log] [-notrack] [-stats]
               [-planner PLANNER | --fondp | --fondpshow | --fondpnoshow | --strong | --strongcyclic | --dual | --index] [-k K] [--expgoal] [--atoms] [-n N] [-t T]
               [-timeout TIMEOUT] [-memout MEMOUT]
               [experiments [experiments ...]]
...
```

You can check it has been installed as follows:

```shell
$ pip ip freeze | grep fond
-e git+git@github.com:idrave/FOND-ASP.git@a1777855e1b31723601490f0522b704adc39afd0#egg=fcfondplanner
```

To remove the package:

```shell
$ pip uninstall fcfondplanner
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

## PDDL and ASP specifications of FOND+ problems

### PDDL specifications

To specify a FOND+ task, the PDDL is extended to allow the specification of  conditional fairness.

A **fairness expression** allow to define PDDL problems with _custom_ fairness assumptions for the FOND-ASP planner and has the form:

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

### ASP Encoding

It is also possible to specify a FOND+ problem directly in ASP format, by means of a set of facts using the following distinguished atoms:

* `state(S)`: `S` is a state
* `initialState(S)`: `S` is the initial state
* `goal(S)`: `S` is a goal state
* `action(A)`: `A` is an action
* `transition(S1, A, S2)`: there is a transition from state `S1` to state `S2` applying action `A`
* `con_A(A, I)`: action `A` belongs to set of constraints `A_I`
* `con_B(A, I)`: action `A` belongs to set of constraints `B_I`

Inf act, when the system receives (extended) PDDL files, the problem is first translated to an ASP encoding using the above atoms.

The **output of a solver** should be atoms `policy(S, A)` specifying the action `A` to be applied in state `S`. In our sample experiments, the states and actions are represented as integers. To make the output more human readable, one can include the following rule in our program:

```asp
#show policy(State, Action): policy(IdS, IdA), id(state(State), IdS), id(action(Action), IdA), reach(IdS).
```

Where `id/2` symbols are generating automatically by the PDDL parser to describe the states and actions assigned to each integer ID.

## Running FOND-ASP

Once installed as an editable module, we can execute the planner by using `-m fcfond.main` from anywhere:

```bash
$ python -m fcfond.main -h
```

The most common way to use the planner to solve FOND+ tasks is by running it over input PDDL files as follows:

```shell
$ python -m fcfond.main -pddl DOMAIN PROBLEM
```

where `DOMAIN` and `PROBLEM` are the PDDL files encoding the planning domain and problem to be solved.

For example, to solve the 7th problem of the Doors benchmark using the default FOND+ solver implemented in `fcfond/planner_clingo/fondplus_show_pretty.lp`, show the statistics (`-stats`), and leave the result files under folder `output.fondasp/`:

```shell
$ python -m fcfond.main -stats -out output.fondasp -pddl fcfond/domains/pddl/fond-sat/doors/domain.pddl fcfond/domains/pddl/fond-sat/doors/p07.pddl 

Namespace(atoms=False, clingo=None, experiments=[], expgoal=False, k=None, list=None, log=False, memout=8000000000.0, n=1, notrack=False, out=None, pddl=['fcfond/domains/pddl/fond-sat/doors/domain.pddl', 'fcfond/domains/pddl/fond-sat/doors/p07.pddl'], planner=None, stats=True, t=1, timeout=1800.0)
Pddl processed. Start ASP solver.
Command ['clingo', PosixPath('/mnt/ssardina-research/planning/FOND-ASP.git/fcfond/planner_clingo/fondplus_show_pretty.lp'), 'output/proc_p07.lp', '-n', '1', '-t', '1', '--single-shot']
ASP Solved. Processing output
Output processed.
Problem: p07
States: 1530
Actions: 16
Pre-processing time: 2.699
Sat: True
Models: 1
Calls: 1
Time: 17.26
Solve Time: 0.07
1st Model Time: 0.06
Unsat Time: 0.02
CPU Time: 17.258
Result: True
Max Memory: 628.396

  Problem  States  Actions  Pre-processing time   Sat Models  Calls   Time  Solve Time  1st Model Time  Unsat Time  CPU Time Result  Max Memory
0     p07    1530       16                2.699  True      1      1  17.26        0.07            0.06        0.02    17.258   True     628.396
```

In this example, the solution will amount to a strong plan because no conditional fairness pairs have been specified. See below to use a specialized version that will solve it much faster.

When given a PDDL file as above, the system will run in two phases. In the _first phase_, the PDDL is translated into an ASP flat encoding of the state space. By default, the number of states encoded is incrementally tracked and reported; that can be switched off via `-notrack`. In the _second phase_, the encoded flat representation of the PDDL problem is solved against a FOND+ planner solver (or a specialized one if option `-planner` is used).

After execution, the planner will leave the following files in the output folder (`output/` by default, but can be specified via option `-out`):

* `proc_p07.lp`: the full planning problem encoded as a set of ASP facts; see below for atoms used. This can be re-used to run the planner directly on this encoding and avoid a re-encoding.
* `stdout-encode.txt`: the standard output of the encoding phase from PDDL to ASP.
* `stdout-asp.txt`: the standard output of the ASP solver, which shows a successful policy, if any has been found, via atoms `policy(S, A)` specifying the action `A` to be applied in state `S`.
* `metrics.csv`: the statistic of the solving task (e.g., time, no of models, etc.).

When using option `-stats` as above, stats will be reported including various time statistics:

* `Pre-processing Time`: time FOND-ASP took to pre-process the input before sending it to ASP solver.
* `Time`: total time that Clingo ASP system took to run, as reported in `stdout-asp.txt` by Clingo itself. This includes Clingo pre-processing, grounding, and solving time of the input ASP.
* `CPU Time`: Clingo solve time considering all threads used. When only one thread is used, it should equal `Time`.
* `Solve Time`: time that took Clingo took to just _solve_ the problem, without considering Clingo's pre-procesing and grounding.
* `1st Model Time`: time it took Clingo to find the first solution model.

There are two major aspects that can be changed in the above default use of FOND-ASP:

1. Specify a specialized planner solver via option `-planner`. There are a few of these planners available.
2. Run the system directly on a Clingo ASP flat encoding of the planning task via option `-clingo`. This will save the pre-processing time of converting the PDDL specification into an ASP flat encoding.

## Panners/Solvers available

The **default** FOND+ system of the planner uses ASP planner program `fcfond/planner_clingo/fondplus_pretty.lp` and pretty prints the policy found as rules `S ==> A`. This solver takes a FOND+ problem, including conditional fairness specifications.

We can specify alternative planner solvers via the option `--planner PLANNER`. The deafult system is equivalent to running:

```shell
$ python -m fcfond.main -planner fcfond/planner_clingo/fondplus_show_pretty.lp -pddl DOMAIN PROBLEM
```

The following are alternative FOND+ planners that just print the resulting policy differently:

* `fcfond/planner_clingo/fondplus.lp`: only the `policy/2` fraction of the model is reported.
* `fcfond/planner_clingo/fondplus_noshow.lp`: silent solver, nothing is reported.
* `fcfond/planner_clingo/fondplus_show.lp`: like `fondplus.lp` but grounding the showing part independently and after solving the main program. Seems to sometime run faster.

Finally, planner solver `fcfond/planner_clingo/fondp_index.lp` is a **bounded version** of the FOND+ solver that uses a bound `k` on the grounding of the program to limit the recursive procedure searching for terminating states. Such bound can be specified using command line option `-k N`, where `N` is a positive integer. Note that this planner may not find a valid policy if the bound is too low for the problem being solved.

Specialized planners are provided to solve FOND problems under the two standard semantics: strong plans under adversarial semantics and strong-cyclic plans under state-action fairness, as well as dual-FOND (mixing adversarial and fair actions). The benchmark from the FOND-SAT planning system are included in this repo under [fcfond/domains/pddl/fond-sat/](fcfond/domains/pddl/fond-sat).

### Pure Strong under adversarial semantics

The ASP program `fcfond/planner_clingo/specialized/planner_strong.lp` provides a specialized planner under _pure strong planning under adversarial semantics_ for non-determinism. Solutions are _conditional_ plans where the length of each run to the goal is bounded in advanced.

The use of this solver can be activated by using option `--strong` directly:

```shell
$ python -m fcfond.main --strong -pddl DOMAIN PROBLEM 
```

This is equivalent to running:

```shell
$ python -m fcfond.main --planner fcfond/planner_clingo/specialized/planner_strong.lp -pddl DOMAIN PROBLEM
```

For example, if we re-run the above problem 7 of Doors with this specialized solver:

```shell
$ python -m fcfond.main --strong -stats -out output.fondsat/ -pddl fcfond/domains/pddl/fond-sat/doors/domain.pddl fcfond/domains/pddl/fond-sat/doors/p07.pddl     
Namespace(atoms=False, clingo=None, experiments=[], expgoal=False, k=None, list=None, log=False, memout=8000000000.0, n=1, notrack=False, out='output.fondsat/', pddl=['fcfond/domains/pddl/fond-sat/doors/domain.pddl', 'fcfond/domains/pddl/fond-sat/doors/p07.pddl'], planner=PosixPath('/mnt/ssardina-research/planning/FOND-ASP.git/fcfond/planner_clingo/specialized/planner_strong.lp'), stats=True, t=1, timeout=1800.0)
Pddl processed. Start ASP solver.
Command ['clingo', PosixPath('/mnt/ssardina-research/planning/FOND-ASP.git/fcfond/planner_clingo/specialized/planner_strong.lp'), 'output.fondsat/proc_p07.lp', '-n', '1', '-t', '1', '--single-shot']
ASP Solved. Processing output
Output processed.
Problem: p07
States: 1530
Actions: 16
Pre-processing time: 2.736
Sat: True
Models: 1+
Calls: 1
Time: 0.401
Solve Time: 0.0
1st Model Time: 0.0
Unsat Time: 0.0
CPU Time: 0.401
Result: True
Max Memory: 62.316

  Problem  States  Actions  Pre-processing time   Sat Models  Calls   Time  Solve Time  1st Model Time  Unsat Time  CPU Time Result  Max Memory
0     p07    1530       16                2.736  True     1+      1  0.401         0.0             0.0         0.0     0.401   True      62.316
```

Observe this takes significantly less than when the full FOND+ solver has been used as per above.

Importantly, when this specialization is used, no `(:fairness )` statements are required, as the semantics is already fixed in the planner used (as adversarial semantics).

Nonetheless, one can still solve strong standard FOND planning problems by just running the _default_ FOND+ planner solver on the original (non-deterministic) PDDL files with no `(:fairness :a ... b: ...)` clauses: every non-determinism is assumed of _adversarial_ type. 

### Pure Strong-cyclic under state-fair semantics

A specialized planner for solving FOND problem under the state-action fairness assumption, and under which plans are strong-cyclic policies, is provided by ASP program `fcfond/planner_clingo/specialized/planner_strongcyclic.lp`

So, to solve a FOND problem using the specialized planner for _**pure strong-cyclic**_ planning (state-action fairness) semantics we can use the `--strongcyclic` option:

```shell
$ python -m fcfond.main --strongcyclic -pddl DOMAIN PROBLEM 
```

which is equivalent to:

```shell
$ python -m fcfond.main --planner fcfond/planner_clingo/specialized/planner_strongcyclic.lp -pddl DOMAIN PROBLEM 
```

For example:

```shell
$ python -m fcfond.main --strongcyclic -pddl fcfond/domains/pddl/fond-sat/beam-walk/domain.pddl fcfond/domains/pddl/fond-sat/beam-walk/p01.pddl
```

As with strong planning, when this specialization is used, no `(:fairness )` statements are required, as the semantics is already fixed in the planner used (as adversarial semantics).

Nonetheless, one can still solve standard strong-cyclic FOND problems by just running the _default_ FOND+ planner solver on the original (non-deterministic) PDDL files extended to include corresponding fairness constraints for each non-deterministic ground action `a` of the form `[A={a},B=empty]`. This means one `(:fairness :a GROUND_ACTION)` for each _ground_ action in the problem needs to be included.

### Dual FOND: mix of adversarial and fair actions

Finally, a specialized planner for Dual-FOND planning is provided in  `fcfond/planner_clingo/specialized/dualfond.lp`. This planner solver can be directly activated by using option `--dual`.

This is a conditional planner for Dual-FOND problems, where some actions are adversarial and other actions are fair (in all states).

The fair actions must be indicated in the PDDL description of the problem using `(:fairness :a GROUND_ACTION)` clauses. Any action not appearing in any such clause will be assumed to be adversarial.

## Running against an ASP encoding

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
* `metrics.csv`: contains a summary of several performance metrics.
* `.lp` files with Clingo symbols corresponding to the input domains.

Here is an example running the QNP problems:

```shell
$ python -m fcfond.main qnp     
qnp
['clear_qnp', 'on_qnp', 'gripper_qnp', 'delivery_qnp']
clear_qnp
Pddl processed
['clingo', PosixPath('/home/ssardina/git/soft/planning/FOND/FOND-ASP.git/fcfond/planner_clingo/fondplus.lp'), 'output/qnp/all/proc_clear.lp', '-n', '1', '-t', '1']
Status:  Finished
on_qnp
Pddl processed
['clingo', PosixPath('/home/ssardina/git/soft/planning/FOND/FOND-ASP.git/fcfond/planner_clingo/fondplus.lp'), 'output/qnp/all/proc_on.lp', '-n', '1', '-t', '1']
Status:  Finished
gripper_qnp
Pddl processed
['clingo', PosixPath('/home/ssardina/git/soft/planning/FOND/FOND-ASP.git/fcfond/planner_clingo/fondplus.lp'), 'output/qnp/all/proc_gripper.lp', '-n', '1', '-t', '1']
Status:  Finished
delivery_qnp
Pddl processed
['clingo', PosixPath('/home/ssardina/git/soft/planning/FOND/FOND-ASP.git/fcfond/planner_clingo/fondplus.lp'), 'output/qnp/all/proc_delivery.lp', '-n', '1', '-t', '1']
Status:  Finished
```