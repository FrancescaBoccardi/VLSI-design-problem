# VLSI-design-problem

In recent years, Very Large-Scale Integration (VLSI) has been a well known problem: it is the process of organizing millions or even billions of electronic components in order to fit more of them in a given area.
Considering the increasing number of components that are involved, it is necessary to address these problems with smart and efficient techniques.

This repository describes three different Combinatorial Optimization approaches to the VLSI problem:

* Constraint Programming (CP)
* Satisfiability Modulo Theories (SMT)
* Mixed Integer-Linear Programming (MIP)

## Repository structure

````
.
├── CP                      
|   ├── instances                     # Input instances in dzn format 
|   ├── out                             
|   │   ├── out_no_rotations          # Output .txt files containing the solutions for the CP no-rotation model
|   │   ├── out_rotations             # Output .txt files containing the solutions for the CP rotation model
|   ├── plots                             
|   │   ├── plots_no_rotations        # Images to visualize the feasible solutions for the CP no-rotation model 
|   │   ├── plots_rotations           # Images to visualize the feasible solutions for the CP rotation model
|   ├── src                             
|   │   ├── CP.py                     # Script to launch the CP models, contained in the .mzn files 
|   │   ├── CP_no_rotations.mzn       # CP no rotation model
|   │   ├── CP_rotations.mzn          # CP rotation moodel
├── SMT                      
|   ├── instances                     # Input instances in dzn format 
|   ├── out                             
|   │   ├── out_no_rotations          # Output .txt files containing the solutions for the SMT no-rotation model
|   │   ├── out_rotations             # Output .txt files containing the solutions for the SMT rotation model
|   ├── plots                             
|   │   ├── plots_no_rotations        # Images to visualize the feasible solutions for the SMT no-rotation model 
|   │   ├── plots_rotations           # Images to visualize the feasible solutions for the SMT rotation model
|   ├── src                             
|   │   ├── SMT.py                    # Script to create and launch the SMT models
├── MIP                      
|   ├── instances                     # Input instances in dzn format 
|   ├── out                             
|   │   ├── out_no_rotations          # Output .txt files containing the solutions for the MIP no-rotation model
|   │   ├── out_rotations             # Output .txt files containing the solutions for the MIP rotation model
|   ├── plots                             
|   │   ├── plots_no_rotations        # Images to visualize the feasible solutions for the MIP no-rotation model 
|   │   ├── plots_rotations           # Images to visualize the feasible solutions for the MIP rotation model
|   ├── src                             
|   │   ├── MIP.py                    # Script to create and launch the MIP models
├── README.md
├── VLSI_report.pdf                   # Report of the whole project  
````

## Requirements

Each approach requires specific installations.

CP:
* [Python](https://www.python.org/)
* [MiniZinc](https://www.minizinc.org/)
* [Minizinc Python](https://minizinc-python.readthedocs.io/en/latest/getting_started.html)
* [Matplotlib](https://matplotlib.org/)

SMT:
* [Python](https://www.python.org/)
* [Matplotlib](https://matplotlib.org/)
* [z3-solver](https://pypi.org/project/z3-solver/)
* [NumPy](https://numpy.org/)

MIP:
* [Python](https://www.python.org/)
* [Matplotlib](https://matplotlib.org/)
* [Gurobi](https://www.gurobi.com/), combined with an [Academic License](https://www.gurobi.com/academia/academic-program-and-licenses/)
* [gurobipy](https://pypi.org/project/gurobipy/)

## Usage

In order to reproduce the experiments, simply open a terminal in the correspondent working directory and run:
````
$ python CP.py
````
````
$ python SMT.py
````
````
$ python MIP.py
````
By lanching the .py files, output files and images to visualize the solutions will be automatically created and saved respectively into ````out```` and  ````plots```` folders.

## Authors

The project has been realized by:

* Francesca Boccardi ([FrancescaBoccardi](https://github.com/FrancescaBoccardi))
* Luigi Podda ([lupodda](https://github.com/lupodda))
