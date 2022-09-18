from matplotlib.patches import Rectangle
from random import randint
from datetime import timedelta
import os
from timeit import default_timer as timer
from minizinc import Solver, Instance, Model
import matplotlib.pyplot as plt
import re

#================================================== Input-Output methods =================================================================

def load_data(line):
    line = line.split('[')[1]
    line = line.split(']')[0]
    line = line.split(',')
    return [int(n) for n in line]


def write_output(width, n_circuits, dx, dy, x_sol, y_sol, height, output_file, elapsed_time, rotation, rotations=None):

    with open(output_file, 'w+') as out_file:

        out_file.write('{} {}\n'.format(width, height))
        out_file.write('{}\n'.format(n_circuits))

        for i in range(n_circuits):
            out_file.write('{} {} {} {} '.format(dx[i], dy[i], x_sol[i], y_sol[i]))

            if rotation:
                if(rotations[i]):
                    out_file.write('Rotated\n')
                else:
                    out_file.write('Not rotated\n')
            else:
                out_file.write('\n')

        
        out_file.write("----------\n==========\n")

        out_file.write('{}'.format(elapsed_time))

def plot(x_sol, y_sol, d, r, w, n_ins, rotation):

    n = len(x_sol)
    colors = []

    for i in range(n):
        colors.append('#%06X' % randint(0, 0xFFFFFF))

    fig, ax = plt.subplots()

    for i in range(n):
        ax.plot()
        ax.add_patch(Rectangle((x_sol[i], y_sol[i]), r[i], d[i] ,color=colors[i], alpha=0.5))

    if rotation:
        plt.savefig('../plots/plots_rotations/ins-' + str(n_ins) + '-plot.png')
    else:
        plt.savefig('../plots/plots_no_rotations/ins-' + str(n_ins) + '-plot.png')


#============================================== Solving instances method ========================================================


def solve_instance(w, r, d, n, n_ins, rotation):

    if rotation:

        # Loading the rotation model
        model = Model("./CP_rotations.mzn")

        # Setting the solver
        solver = Solver.lookup("chuffed")

        # Loading data into the model
        instance = Instance(solver, model)
        instance["w"] = w
        instance["n"] = n
        instance["r"] = r
        instance["d"] = d

        # Running the model
        start_time = timer()
        mznout = instance.solve(timeout=timedelta(seconds=301), free_search=True)
        solve_time = timer() - start_time

        # Solution
        x_sol = mznout.solution.x
        y_sol = mznout.solution.y
        x_dim = mznout.solution.x_dim
        y_dim = mznout.solution.y_dim
        height_sol = mznout.solution.height
        rot_sol = mznout.solution.rotation

        # Writing solution
        out_dir = "../out/out_rotations/"
        instance_name = "ins-" + str(n_ins)
        out_file = os.path.join(out_dir, instance_name + '-out.txt')
        write_output(w, n, x_dim, y_dim, x_sol, y_sol, height_sol, out_file, solve_time, rotation, rot_sol)
        
        # Plotting the solution
        plot(x_sol, y_sol, y_dim, x_dim, w, n_ins, rotation)

    else:

        # Loading the no-rotation model
        model = Model("./CP_no_rotations.mzn")

        # Setting the solver
        solver = Solver.lookup("chuffed")

        # Loading data into the model
        instance = Instance(solver, model)
        instance["w"] = w
        instance["n"] = n
        instance["r"] = r
        instance["d"] = d

        # Running the model
        start_time = timer()
        mznout = instance.solve(timeout=timedelta(seconds=301), free_search = True)
        solve_time = timer() - start_time

        # Solution
        x_sol = mznout.solution.x
        y_sol = mznout.solution.y
        height_sol = mznout.solution.height

        # Writing solution
        out_dir = "../out/out_no_rotations"
        instance_name = "ins-" + str(n_ins)
        out_file = os.path.join(out_dir, instance_name + '-out.txt')
        write_output(w, n, r, d, x_sol, y_sol, height_sol, out_file, solve_time, rotation)
        
        # Plotting the solution
        plot(x_sol, y_sol, d, r, w, n_ins, rotation)

#=================================================== Running CP models ===================================================


for n_ins in range(1,41):

    f = open('../instances/ins-' + str(n_ins) + ".dzn", "r")
    lines = f.readlines()
    w = int(re.findall(r'\d+', lines[0])[0])
    r = load_data(lines[6])
    d = load_data(lines[4])
    n = len(d)

    print("Solving instance "+str(n_ins))

    # Launch no-rotation model
    solve_instance(w, r, d, n, n_ins, rotation=False)

    # Launch rotation model
    solve_instance(w, r, d, n, n_ins, rotation=True)