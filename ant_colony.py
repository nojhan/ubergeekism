#!/usr/bin/env python

import sys
import math
import random
from collections import Counter


def log( *args ):
    for msg in args:
        sys.stderr.write( str(msg) )
        sys.stderr.write(" ")
        sys.stderr.flush()


def logn( *args ):
    log( *args )
    log("\n")

def tour(lst):
    # consecutive pairs in lst  + last-to-first element
    for a,b in zip(lst, lst[1:] + [lst[0]]):
        yield (a,b)


def euclidian_distance( ci, cj ):
    return math.sqrt( float(ci[0] - cj[0])**2 + float(ci[1] - cj[1])**2 )


def cost( permutation, cost_func, cities ):
    dist = 0
    for i,j in tour(permutation):
        dist += cost_func(cities[i],cities[j])
    return dist


def random_permutation( cities ):
    # like random.shuffle(cities) but on a copy
    return sorted( cities, key=lambda i: random.random())


def initialize_pheromone_matrix( nb_cities, init_value ):
    rows = []
    for i in range(nb_cities):
        cols = []
        for j in range(nb_cities):
            cols.append( init_value )
        rows.append(cols)
    return rows


def choose( cities, last, exclude, pheromones, w_heuristic, w_history ):
    choices = []
    for i,city in enumerate(cities):
        if i in exclude:
            continue
        c = {"city" : i}
        c["history"]   = pheromones[last][i] ** w_history
        c["distance"]  = euclidian_distance( cities[last], city )
        c["heuristic"] = (1.0 / c["distance"]) ** w_heuristic
        c["proba"] = c["history"] * c["heuristic"]
        choices.append(c)
    return choices


def proba_select( choices ):
    s = sum( c["proba"] for c in choices )
    if s == 0.0:
        return random.choice(choices)["city"]

    v = random.random()
    for i,c in enumerate(choices):
        v -= c["proba"] / s
        if v <= 0.0:
            return c["city"]

    return c[-1]["city"]


def greedy_select( choices ):
    c = max( choices, key = lambda c : c["proba"] )
    return c["city"]


def walk( cities, pheromone, w_heuristic, c_greedy ):
    assert( len(cities) > 0 )
    # permutations are indices
    # randomly draw the first city index
    permutation = [ random.randint(0,len(cities)-1) ]
    # then choose the next ones to build the permutation
    while len(permutation) < len(cities):
        choices = choose( cities, permutation[-1], permutation, pheromone, w_heuristic, w_history = 1.0 )
        do_greedy = ( random.random() <= c_greedy )
        if do_greedy:
            next_city = greedy_select( choices )
        else:
            next_city = proba_select( choices )
        permutation.append( next_city )

    # assert no duplicates
    assert( max(Counter(permutation).values()) == 1 )
    return permutation


def update_global( pheromones, candidate, decay ):
    for i,j in tour(candidate["permutation"]):
        value = ((1.0 - decay) * pheromones[i][j]) + (decay * (1.0/candidate["cost"]))
        pheromones[i][j] = value
        pheromones[j][i] = value


def update_local( pheromones, candidate, w_pheromone, init_pheromone ):
    for i,j in tour(candidate["permutation"]):
        value = ((1.0 - w_pheromone) * pheromones[i][j]) + (w_pheromone * init_pheromone)
        pheromones[i][j] = value
        pheromones[j][i] = value


def search( max_iterations, nb_ants, decay, w_heuristic, w_pheromone, c_greedy, cities):
    best = { "permutation" : random_permutation(range(len(cities))) }
    best["cost"] = cost( best["permutation"], euclidian_distance, cities )
    init_pheromone = 1.0 / float(len(cities)) * best["cost"]
    pheromone = initialize_pheromone_matrix( len(cities), init_pheromone )
    for i in range(max_iterations):
        log( i )
        solutions = []
        for j in range(nb_ants):
            log( "." )
            candidate = {}
            candidate["permutation"] = walk( cities, pheromone, w_heuristic, c_greedy )
            candidate["cost"] = cost( candidate["permutation"], euclidian_distance, cities )
            if candidate["cost"] < best["cost"]:
                best = candidate
            update_local( pheromone, candidate, w_pheromone, init_pheromone )
        update_global( pheromone, best, decay )
        logn( best["cost"] )

    return best


if __name__ == "__main__":
    max_it = 40
    num_ants = 10
    decay = 0.1
    c_heur = 2.5
    c_local_phero = 0.1
    c_greed = 0.9

    print "Berlin euclidian TSP"
    berlin52 = [[565,575],[25,185],[345,750],[945,685],[845,655],
          [880,660],[25,230],[525,1000],[580,1175],[650,1130],[1605,620],
          [1220,580],[1465,200],[1530,5],[845,680],[725,370],[145,665],
          [415,635],[510,875],[560,365],[300,465],[520,585],[480,415],
          [835,625],[975,580],[1215,245],[1320,315],[1250,400],[660,180],
          [410,250],[420,555],[575,665],[1150,1160],[700,580],[685,595],
          [685,610],[770,610],[795,645],[720,635],[760,650],[475,960],
          [95,260],[875,920],[700,500],[555,815],[830,485],[1170,65],
          [830,610],[605,625],[595,360],[1340,725],[1740,245]]

    best = search( max_it, num_ants, decay, c_heur, c_local_phero, c_greed, berlin52 )
    print best["cost"], best["permutation"]

