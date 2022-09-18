import os
from z3 import *
from z3 import And, Or, Bool, Int, Optimize, sat, If, Implies
import re
import numpy as np
import time
from matplotlib import pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.pyplot import figure
from random import randint


#================================================== Input-Output methods =================================================================

def load_data(line):
    line = line.split('[')[1]
    line = line.split(']')[0]
    line = line.split(',')
    return [int(n) for n in line]


def write_output(width, n_circuits, dx, dy, x_sol, y_sol, height, output_file, elapsed_time, time_expired, rotation, rotations=None):

    with open(output_file, 'w+') as out_file:

        if time_expired:
            out_file.write("Time expired")

        else:
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


#================================================= Models' constraints methods ================================================

def z3_max(vector):
    maximum = vector[0]
    for value in vector[1:]:
        maximum = If(value > maximum, value, maximum)
    return maximum


def z3_cumulative(start, duration, resources, total):
    cumulative = []
    for u in duration:
        cumulative.append(
            sum([If(And(start[i] <= u, u < start[i] + duration[i]), resources[i], 0)
                 for i in range(len(start))]) <= total
        )
    return cumulative

def lex(x, y):
    lex = [And([x[0] <= y[0]] + [Implies(And([x[i] == y[i] for i in range(k)]), x[k] <= y[k]) for k in range(1, len(x))])]
    return lex

def no_overlap(x, y, r, d, n):
    no_overlap = []
    for i in range(n):
        for j in range(n):
            if (i!=j):
                no_overlap.append(Or((x[i]+r[i]<=x[j]), (x[j]+r[j]<=x[i]), (y[i]+d[i]<=y[j]), (y[j]+d[j]<=y[i])))
    return no_overlap


#============================================== Solving instances method ========================================================


def solve_instance(w, r, d, n, n_ins, rotation):

    if rotation:
        
        # Variables
        x = [Int(f"x{i}") for i in range(n)]
        y = [Int(f"y{i}") for i in range(n)]
        height = z3_max([dy[i] + y[i] for i in range(n)])
        dx = [Int(f"x_dim{i}") for i in range(n)]
        dy = [Int(f"y_dim{i}") for i in range(n)]
        rotation = [Bool(f"rot{i}") for i in range(n)]

        #Bounds
        levels = ((sum(r) // w) + 1)*2 
        d_sort = sorted(d)
        h_max = sum([d_sort[n-1-i] for i in range(min(levels,n))])
        h_min = sum(d[i]*r[i] for i in range(n)) / w  

        # Domains
        domain_x = [x[i]>=0 for i in range(n)]
        domain_y = [y[i]>=0 for i in range(n)]
        domain_height = [And(height>=h_min, height<=h_max)]
        
        # Constraints
        max_w = [z3_max([dx[i] + x[i] for i in range(n)]) <= w]
        no_over = no_overlap(x, y, dx, dy, n)
        cumulative_x = z3_cumulative(y,dy,dx,w)
        rot_constraint = [If(rotation[i], And(dy[i]==r[i], dx[i]==d[i]), And(dy[i]==d[i], dx[i]==r[i])) for i in range(n)]
        square = [Implies(d[i]==r[i], rotation[i]==False) for i in range(n)]
        break_x = [w-x[i]-dx[i] for i in range(n)]        
        sym_break_x = lex(x, break_x)


        # Solver
        
        opt = Optimize()
        opt.add(domain_x + domain_y + no_over + max_w + cumulative_x + sym_break_x  + rot_constraint  + domain_height + square)
        opt.set("timeout", 300000)
        opt.minimize(height)

        t0 = time.time()
        check = opt.check()
        elapsed_time = time.time() - t0

        # Solution

        x_sol = []
        y_sol = []
        dx_sol = []
        dy_sol = []
        height_sol = ""
        rot_sol = []

        if check == sat:
            time_exp = False
            model = opt.model()
            for i in range(n):
                x_sol.append(model.evaluate(x[i]).as_long())
                y_sol.append(model.evaluate(y[i]).as_long())
                dx_sol.append(model.evaluate(dx[i]).as_long())
                dy_sol.append(model.evaluate(dy[i]).as_long())


            for i in range(n):
                if model.evaluate(rotation[i]) == True:
                    rot_sol.append(True)
                elif model.evaluate(rotation[i]) == False:
                    rot_sol.append(False)

            height_sol = model.evaluate(height).as_string()
            
            # Plotting the solution
            
            plot(x_sol, y_sol, dy_sol, dx_sol, w, n_ins, rotation)

        else:
            time_exp = True

        # Writing solution

        out_dir = "../out/out_rotations/"
        instance_name = "ins-" + str(n_ins)
        out_file = os.path.join(out_dir, instance_name + '-out.txt')

        write_output(w, n, dx_sol, dy_sol, x_sol, y_sol, height_sol, out_file, elapsed_time, time_exp, rotation, rot_sol)

        
    else:
        
        # Variables
        x = [Int(f"x{i}") for i in range(n)]
        y = [Int(f"y{i}") for i in range(n)]
        height = z3_max([d[i] + y[i] for i in range(n)])

        #Bounds
        levels = ((sum(r) // w) + 1)*2 
        d_sort = sorted(d)
        h_max = sum([d_sort[n-1-i] for i in range(min(levels,n))])
        h_min = sum(d[i]*r[i] for i in range(n)) / w

        # Domains
        domain_x = [x[i]>=0 for i in range(n)]
        domain_y = [y[i]>=0 for i in range(n)]
        domain_height = [And(height>=h_min, height<=h_max)]

        # Constraints
        max_w = [z3_max([r[i] + x[i] for i in range(n)]) <= w]
        no_over = no_overlap(x, y, r, d, n)
        cumulative_x = z3_cumulative(y,d,r,w)

        # Solver
        opt = Optimize()
        opt.add(domain_x + domain_y + no_over + max_w + cumulative_x + domain_height)
        opt.set("timeout", 300000)
        opt.minimize(height)

        t0 = time.time()
        check = opt.check()
        elapsed_time = time.time() - t0

        # Solution
        x_sol = []
        y_sol = []
        height_sol = ""

        if check == sat:
            time_exp = False
            model = opt.model()
            for i in range(n):
                x_sol.append(model.evaluate(x[i]).as_long())
            for i in range(n):
                y_sol.append(model.evaluate(y[i]).as_long())

            height_sol = model.evaluate(height).as_string()
            
            # Plotting the solution

            plot(x_sol, y_sol, d, r, w, n_ins, rotation)

        else:
            time_exp = True

        # Writing solution

        out_dir = "../out/out_no_rotations"
        instance_name = "ins-" + str(n_ins)
        out_file = os.path.join(out_dir, instance_name + '-out.txt')

        write_output(w, n, r, d, x_sol, y_sol, height_sol, out_file, elapsed_time, time_exp, rotation)


#=================================================== Running SMT models ===================================================

for n_ins in range(1,41):

    f = open('../instances/ins-' + str(n_ins) + ".dzn", "r") 
    lines = f.readlines()
    w = int(re.findall(r'\d+', lines[0])[0])
    r = load_data(lines[6])
    d = load_data(lines[4])
    n = len(d)

    # Pre-processing: ordering instances by decreasing area
    areas = []

    for i in range(n):
        areas.append(d[i]*r[i])

    sorted_idx = np.argsort(areas)[::-1]

    d_sort = []
    r_sort = []

    for i in sorted_idx:
       d_sort.append(d[i])
       r_sort.append(r[i])

    print("Solving instance "+str(n_ins))

    # Launch no-rotation model
    solve_instance(w, r_sort, d_sort, n, n_ins, rotation=False)

    # Launch rotation model
    solve_instance(w, r_sort, d_sort, n, n_ins, rotation=True)