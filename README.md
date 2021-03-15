# FOND-PLUS

Experiments for FOND+ using ASP Clingo encoding for the planner.

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

```bash
git clone https://github.com/idrave/fond-asp.git
cd fond-asp
pip install -r requirements.txt
pip install -e .
```

### Using a Python Pipenv environment

You might want to apply the above steps inside an independent python environment. Here is one way using [Pipenv](https://pypi.org/project/pipenv/).

First install Clingo, by compiling and installing it via CMAKE as per instructions.

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

## PDDL for FOND+ problems

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

## Running the planner

After setting up requirements, you can run experiments using the ASP FOND+ planner with command:

```bash
python -m fcfond.main [EXPERIMENTS] -out OUTPUT
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
- seq`uential`
  - `sequentialXX`, for `XX` from `02` to `10`
- `nested`
  - `nestedXX`, for `XX` from `02` to `10`
- `unfair_qnp`: QNPs without terminating solution
- `fond_sat`: several domains of pure strong and pure strong cyclic planning

To get a list of more available experiments type

```bash
python -m fcfond.main -list LIST
```

Where `LIST` can be one of the experiment lists above.

The result will be left under folder `OUTPUT` and will include:

- `stdout.txt`: file containing the standard output given by Clingo solver when run over the domains. This shows the resulting policy, among other types of information.
- `metrics.csv`: contains a summary of several performance metrics
- `.lp` files with Clingo symbols corresponding to the input domains

The planner can also be run over any input pddl files using:

```bash
python -m fcfond.main -pddl [DOMAIN PROBLEM]
```

Passing as argument a sequence of domain and problem .pddl files.

To see more options available run

```bash
python -m fcfond.main -h
```

### Using a different Clingo encoding

If you wish to test a different variation of the ASP planner encoding, you can do it using:

```bash
python -m fcfond.main [EXPERIMENTS] -planner [PLANNER]
```

Giving as input the path of the `.lp` file with a Clingo planner. Such Clingo encoding could expect to receive as input atoms:

- `state(S)`: `S` is a state
- `initialState(S)`: `S` is the initial state
- `goal(S)`: `S` is a goal state
- `action(A)`: `A` is an action
- `transition(S1, A, S2)`: there is a transition from state `S1` to state `S2` applying action `A`
- `con_A(A, I)`: action `A` belongs to set of constraints `A_I`
- `con_B(A, I)`: action `A` belongs to set of constraints `B_I`

The output should be atoms `policy(S, A)` specifying the action A to be applied in state S. In out sample experiments the states and actions are represented as integers. To make the output more human readable, we include the following rule in our program:

```#show policy(State, Action): policy(IdS, IdA), id(state(State), IdS), id(action(Action), IdA), reach(IdS).```

Where id/2 symbols are generating automatically by the PDDL parser to describe the states and actions assigned to each integer ID.

You could also run a variation of the planner using Clingo directly over an `.lp` file specifying the problem domain as:

```bash
clingo PLANNER DOMAIN
```

### Running standard FOND problems

The FOND+ `asplanner` system can be used to solve _standard_ (i.e., non-dual) FOND problems in which either an adversarial or state-fair view of non-deterministic effect is assumed.

As usual, for adversarial FOND, one seeks _strong_ plan solutions; whereas for FOND under state-fairness assumption, one looks for _strong-cyclic_ plan solutions. 

Two _specialized_ versions the base system, via `--strong` and `--strongcyclic`, are provided to solve these problems.

The benchmark from the FOND-SAT planning system can be found [here](fcfond/domains/pddl/fond-sat) in this repo.

#### FOND problem under adversarial semantics

To solve standard FOND problems under the _adversarial semantics_ (and hence look for strong solution plans) one can either:

1. Use a _specialized_ version of the planner to _pure strong_ with the PDDL file of the FOND problem "as is" (i.e., with no modifications):

    ```bash
    python -m fcfond.main -pddl [DOMAIN PROBLEM] --strong
    ```

    This version will assume effects of ND-actions are not fair and hence will look for strong solutions. For example:

2. Use the planner without any specialization but
with the PDDL file of the FOND problem "as is" (i.e., with no modifications). Note this PDDL will includes _no_ fairness constraints, that is, no `(:fairness :a ... b: ...)` clauses and thus every non-determinism will be adversarial.

As one can see, in both above cases, the PDDL file remains the same and includes no conditional fairness directives.

#### FOND problem under sate-fair semantics

Similarly, to solve standard FOND problems under the _state-fair semantics_ (and hence look for strong-cyclic solution plans) one can either:

1. Use a _specialized_ version of the planner to _strong cyclic_ together with  the PDDL file of the FOND problem as is, with no modifications.

    ```bash
    python -m fcfond.main -pddl [DOMAIN PROBLEM] --strongcyclic
    ```

    This version will assume effects of ND-actions are always fair and hence will look for strong-cyclic solutions.

2. Use the planner without any specialization but over a PDDL version extended to include corresponding fairness constraints for each non-deterministic ground action `a` of the form `[A={a},B=empty]`. This means one `(:fairness :a GROUND_ACTION)` for each _ground_ action in the problem needs to be included.