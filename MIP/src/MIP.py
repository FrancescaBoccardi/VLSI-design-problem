import gurobipy as gp
from gurobipy import GRB
from matplotlib.patches import Rectangle
from matplotlib.pyplot import figure
from random import randint
import os
from timeit import default_timer as timer
import matplotlib.pyplot as plt
import matplotlib.patches as ptc
import re



#================================================== Input-Output methods =================================================================

def load_data(line):
    line = line.split('[')[1]
    line = line.split(']')[0]
    line = line.split(',')
    return [int(n) for n in line]


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


def write_output(width, n_circuits, dx, dy, x_sol, y_sol, height, output_file, elapsed_time, rotation, rotations=None):

    with open(output_file, 'w+') as out_file:

        out_file.write('{} {}\n'.format(width, height))
        out_file.write('{}\n'.format(n_circuits))

        for i in range(n_circuits):
            out_file.write('{} {} {} {} '.format(dx[i], dy[i], x_sol[i], y_sol[i]))

            if rotation:
                if(rotations[i]==1):
                    out_file.write('Rotated\n')
                else:
                    out_file.write('Not rotated\n')
            else:
                out_file.write('\n')

        
        out_file.write("----------\n==========\n")

        out_file.write('{}'.format(elapsed_time))


#============================================== Solving instances method ========================================================


def solve_instance(w, r, d, n, n_ins, rotation):

    # Parameters
    levels = ((sum(r) // w) + 1)*2 
    d_sort = sorted(d)
    h_max = sum([d_sort[n-1-i] for i in range(min(levels,n))]) 
    area_min = sum(d[i]*r[i] for i in range(n))
    area_max = h_max * w
    M = h_max

    if rotation:

        # Creating the MIP model
        m = gp.Model("MIP_rotation")
        m.setParam("TimeLimit", 5*60)

        # Variables
        x = m.addVars(n, ub=w, vtype=GRB.INTEGER, name="x")
        y = m.addVars(n, ub=h_max, vtype=GRB.INTEGER, name="y")
        z = m.addVars(n, n, 4, vtype=GRB.BINARY, name="z")
        height = m.addVar(vtype=GRB.INTEGER, name="height")
        dx = m.addVars(n, vtype=GRB.INTEGER, name="dx")
        dy = m.addVars(n, vtype=GRB.INTEGER, name="dy")
        rot = m.addVars(n, vtype=GRB.BINARY, name="rot")

        # Constraints        
        m.addConstrs(((x[i]+dx[i] <= w) for i in range(n)), "bound_x")
        m.addConstrs(((y[i]+dy[i] <= height) for i in range(n)), "bound_y")

        m.addConstrs(((x[i]+dx[i] <= x[j] + M*z[i,j,0]) for i in range(n) for j in range(i+1,n)), "or1")
        m.addConstrs(((y[i]+dy[i] <= y[j] + M*z[i,j,1]) for i in range(n) for j in range(i+1,n)), "or2")
        m.addConstrs(((x[j]+dx[j] <= x[i] + M*z[i,j,2]) for i in range(n) for j in range(i+1,n)), "or3")
        m.addConstrs(((y[j]+dy[j] <= y[i] + M*z[i,j,3]) for i in range(n) for j in range(i+1,n)), "or4")
        m.addConstrs((gp.quicksum(z[i,j,k] for k in range(4))<=3 for i in range(n) for j in range(n)), "no_overlap")

        area = height * w
        m.addConstr(area >= area_min, "area_lb")
        m.addConstr(area <= area_max, "area_ub")

        m.addConstrs(((dy[i] == rot[i]*r[i] + (1-rot[i])*d[i]) for i in range(n)), "rot_y")
        m.addConstrs(((dx[i] == rot[i]*d[i] + (1-rot[i])*r[i]) for i in range(n)), "rot_x")

        # Objective function
        m.setObjective(height, GRB.MINIMIZE)

        # Solver
        start_time = timer()
        m.optimize()
        solve_time = timer() - start_time

        m.write('MIP_rotation.lp')

        # Solution
        print('')
        print('Solution:')
        print('')

        x_sol = []
        y_sol = []
        rot_sol = []
        dx_sol = []
        dy_sol = []

        for i in range(n):
            x_sol.append(int(m.getVarByName(f"x[{i}]").X))
            y_sol.append(int(m.getVarByName(f"y[{i}]").X))
            rot_sol.append(int(m.getVarByName(f"rot[{i}]").X))
            dx_sol.append(int(m.getVarByName(f"dx[{i}]").X))
            dy_sol.append(int(m.getVarByName(f"dy[{i}]").X))

        height_sol = int(m.ObjVal)

        # Writing solution
        out_dir = "../out/out_rotations/"
        instance_name = "ins-" + str(n_ins)
        out_file = os.path.join(out_dir, instance_name + '-out.txt')

        write_output(w, n, dx_sol, dy_sol, x_sol, y_sol, height_sol, out_file, solve_time, rotation, rot_sol)
        plot(x_sol, y_sol, dy_sol, dx_sol, w, n_ins, rotation)
    
    else:

        # Creating the MIP model
        m = gp.Model("MIP_no_rotation")
        m.setParam("TimeLimit", 5*60) 

        # Variables
        x = m.addVars(n, ub=w, vtype=GRB.INTEGER, name="x")
        y = m.addVars(n, ub=h_max, vtype=GRB.INTEGER, name="y")
        z = m.addVars(n, n, 4, vtype=GRB.BINARY, name="z")
        height = m.addVar(vtype=GRB.INTEGER, name="height")

        
        # Constraints
        m.addConstrs(((x[i]+r[i] <= w) for i in range(n)), "bound_x")
        m.addConstrs(((y[i]+d[i] <= height) for i in range(n)), "bound_y")

        m.addConstrs(((x[i]+r[i] <= x[j] + M*z[i,j,0]) for i in range(n) for j in range(i+1,n)), "or1")
        m.addConstrs(((y[i]+d[i] <= y[j] + M*z[i,j,1]) for i in range(n) for j in range(i+1,n)), "or2")
        m.addConstrs(((x[j]+r[j] <= x[i] + M*z[i,j,2]) for i in range(n) for j in range(i+1,n)), "or3")
        m.addConstrs(((y[j]+d[j] <= y[i] + M*z[i,j,3]) for i in range(n) for j in range(i+1,n)), "or4")
        m.addConstrs((gp.quicksum(z[i,j,k] for k in range(4))<=3 for i in range(n) for j in range(n)), "no_overlap")

        area = height * w
        m.addConstr(area >= area_min, "area_lb")
        m.addConstr(area <= area_max, "area_ub")

        # Objective function
        m.setObjective(height, GRB.MINIMIZE)

        # Solver
        start_time = timer()
        m.optimize()
        solve_time = timer() - start_time

        m.write('MIP_no_rotation.lp')

        # Solution
        print('')
        print('Solution:')
        print('')

        x_sol = []
        y_sol = []

        for i in range(n):
            x_sol.append(int(m.getVarByName(f"x[{i}]").X))
            y_sol.append(int(m.getVarByName(f"y[{i}]").X))

        height_sol = int(m.ObjVal)

        # Writing solution
        out_dir = "../out/out_no_rotations/"
        instance_name = "ins-" + str(n_ins)
        out_file = os.path.join(out_dir, instance_name + '-out.txt')

        write_output(w, n, r, d, x_sol, y_sol, height_sol, out_file, solve_time, rotation)
        plot(x_sol, y_sol, d, r, w, n_ins, rotation)


#=================================================== Running MIP models ===================================================

for n_ins in range(1,5):

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