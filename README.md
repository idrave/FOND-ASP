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

Having clingo installed, you will need to run:
```bash
git clone https://github.com/idrave/aspplanner.git
cd aspplanner
pip install -r requirements.txt
pip install -e .
```

### Using a Python Pipenv environment

You might want to apply the above steps inside an independent python environment. Here is one way using [Pipenv](https://pypi.org/project/pipenv/).

First install `clingo`, by compiling and installing it via CMAKE as per instructions.

Next, install `assplanner` and setup a Python environment:

```bash
$ git clone git@github.com:idrave/aspplanner.git
$ pipenv shell  // create a new environment
(aspplanner) $ 
```

Pipenv would have created a new environment, here named "`aspplanner`". 

Next, install in the environment the dependencies stored in `Pipfile`:

```bash
$ pipenv install
```

Note that `Pipfile` makes reference to the `assplanner` repo via the `git@` protocol, so we require ssh authentication to GitHub for this to work (so that Pipenv will be able to bring the dependency from the repo).

Afte rthis, all the dependencies would have been downlaoded and stored them under a folder like `~/.local/share/virtualenvs/aspplanner-HxHD4kSc`

There is one more thing that needs to be installed: the Python Clingo component into the recently created Pipenv environment. When Clingo was installed, its  Python component where installed under the users' path
`~/.local/lib/python3.8/site-packages/`. This include a `clingo.cpython-38-x86_64-linux-gnu.so` file and `clingo/` folder; copy them both to your Pipenv environment:

```bash
$ cp -a ~/.local/lib/python3.8/site-packages/clingo  ~/.local/share/virtualenvs/aspplanner.git-HxHD4kSc/lib/python3.8/site-packages/
```

Now `clingo` is part of the Pipenv environment, and all is ready to run.

## Running the planner

After setting up requirements, you can run experiments using the ASP FOND+ planner with command:

```bash
python -m fcfond.main [EXPERIMENTS] -out OUTPUT
```

Where `EXPERIMENTS` is one or more available experiments for the planner. Some available experiments and sub-experiments (which can also be run independently)

- qnp
    - clear_qnp
    - on_qnp
    - gripper_qnp
    - delivery_qnp
- ltl
    - list
    - double-list
    - tree
    - graph
    - minlist
    - member-tree
    - swamp
- foot3x2
- sequential
    - sequentialXX, for XX from 02 to 10
- nested
    - nestedXX, for XX from 02 to 10

TODO: display above info from command line option

The result will be left under folder `OUTPUT` and will include:

- `stdout.txt`: file containing the standard output given by Clingo solver when run over the domains. This shows the resulting policy, among other types of information.
- `metrics.csv`: contains a summary of several performance metrics
- `.lp` files with Clingo symbols corresponding to the input domains

The planner can also be run over any input pddl files using:

```bash
python -m fcfond.main -pddl [DOMAIN PROBLEM]
```

Passing as argument a sequence of domain and problem .pddl files.

If you wish to test your own variation of the ASP encoding, you can do it using:

```bash
python -m fcfond.main [EXPERIMENTS] -planner [PLANNER]
```

Giving as input the path of the `.lp` file with a Clingo planner. You could also run it using Clingo directly over an `.lp` file specifying the problem domain as:

```bash
clingo PLANNER DOMAIN
```

To see more options available run

```bash
python -m fcfond.main -h
```

### Running standard FOND problems

One can use the `asplanner` system to solve standard FOND problems (the benchmark from FOND-SAT can be found [here](fcfond/domains/pddl/fond-sat)), and either look for strong or strong-cyclic solutions (under which all effects are assumed "state-fair" as usual).

There are basically four ways of doing so:

1. Specialized the planner to _pure strong_ and use the FOND PDDL as is. This will assume effects of ND-actions are not fair and hence will look for strong solutions.
2. Specialized the planner to _strong cyclic_ and use the FOND PDDL as is. This will assume effects of ND-actions are always fair and hence will look for strong-cyclic solutions.
3. Use the FOND+ `aspplaner` without any specialization over a PDDL version that includes no fairness constraints.
4. Use the FOND+ `aspplaner` without any specialization over a PDDL version that includes corresponding fairness constraints for each non-deterministic action `a` of the form `[A={a},B=empty]`.

While options 1 and 2 require no changes to the PDDL files form the FOND-SAT benchmark, options 3 and 4 require adapting the PDDL to account for the constraints.

For options 1 and 2 run:
```bash
# Option 1
python -m fcfond.main -pddl [DOMAIN PROBLEM] --strong
# Option 2
python -m fcfond.main -pddl [DOMAIN PROBLEM] --strongcyclic
```

To run option 3, run the planner as usual (without --strong or --strongcyclic options) over an input PDDL file that contains no ```(:fairness ...)``` expressions. These usually have the format ```(:fairness :a ... :b ...)```, where the ground actions following ```:a``` and ```:b``` are sets of actions A and B respectively describing a FOND+ constraint [A, B]. These expressions allow to define PDDL problems with custom fairness assumptions for the FONDASP planner.

To run option 4, run the planner as usual over an input PDDL file with an expression of the form ```(:fairness :a GROUND_ACTION)``` for each ground action appearing in the problem. Ground actions are expressed in the form ```(ACTION OBJ1 OBJ2 ... OBJN)```, for an action and the objects grounding its parameters. The action and objects must be defned in the PDDL domain definition.