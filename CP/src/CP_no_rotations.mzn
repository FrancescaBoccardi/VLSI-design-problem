include "globals.mzn";

% Instances data 
int: w; % plate width
int: n; % total number of circuits
array[1..n] of int: d; % circuits height
array[1..n] of int: r; % circuits width

% Area bounds
int: area_min = sum([d[i]*r[i] | i in 1..n]); % minimum plate area
int: area_max = h_max * w; % maximum plate area

% Height bounds
int: h_min = area_min div w; % minimum plate height
int: levels = ((sum(r) div w) + 1)*2;
array[1..n] of int: d_sort = sort(d); 
int: h_max = sum([d_sort[n+1-i] | i in 1..min(levels,n)]); % maximum plate height

% Circuits coordinates bounds
int: x_max = w-min(r);
int: y_max = h_max-min(d);

% Variables
array [1..n] of var 0..x_max: x; % bottom left x coordinates of circuits
array [1..n] of var 0..y_max: y; % bottom left y coordinates of circuits
var area_min..area_max: area = height * w; % plate area
var h_min..h_max : height; % plate height

% Constraints
constraint forall(i in 1..n)(y[i]+d[i] <= height);
constraint forall(i in 1..n)(x[i]+r[i] <= w);
constraint cumulative(y,d,r,w);
constraint cumulative(x,r,d,height); 
constraint diffn(x,y,r,d);
constraint lex_lesseq([x[i] | i in 1..n], [ w - x[i] - r[i] | i in 1..n]); % simmetries breaking

% Search strategy
solve :: seq_search([
    int_search(y, first_fail, indomain_min),
    int_search(x, first_fail, indomain_min),
    int_search([height], input_order, indomain_min)])
    minimize height;