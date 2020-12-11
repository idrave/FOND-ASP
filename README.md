# FOND-PLUS

Experiments for FOND+ using ASP Clingo encoding for the planner.


## Setup

To run the system, you will need to have Clingo installed. In [Potassco](https://potassco.org/clingo/) webpage you can find information about how to set it up. The recommended installation is through a Conda environment running:


```bash
conda install -c potassco clingo
```

Independently of the setup method used, you should be able to run
```bash
clingo -h
```
from command line to run the planner.

You will need to do a minimal setup running, which you might want to do in an independent python environment:
```bash
pip install -r requirements.txt
pip install -e .
```
from the directory in which you have cloned the repo.

## Running the planner

After setting up requirements, you can run experiments using the ASP FOND+ planner with command:
```bash
python -m fcfond.main [EXPERIMENTS] -out OUTPUT
```

Where <code>EXPERIMENTS</code> is one or more available experiments for the planner and <code>OUTPUT</code> is an output directory. Some possible values for this argument are:
- qnp
- ltl
- foot3x2
- sequential
- nested
The output will include:
- stdout.txt: file containing the standard output given by Clingo solver when run over the domains. This shows the resulting policy, among other types of information
- metrics.csv: contains a summary of several performance metrics
- Output .lp files with Clingo symbols corresponding to the input domains
The planner can also be run over any input pddl files using:
```bash
python -m fcfond.main -pddl [DOMAIN PROBLEM]
```
Passing as argument a sequence of domain and problem .pddl files.
If you wish to test your own variation of the ASP encoding, you can do it using:
```bash
python -m fcfond.main [EXPERIMENTS] -planner [PLANNER]
```
Giving as input the path of the .lp file with a Clingo planner. You could also run it using Clingo directly over an .lp file specifying the problem domain as:
```bash
clingo PLANNER DOMAIN
```
To see more options available run
```bash
python -m fcfond.main -h
```