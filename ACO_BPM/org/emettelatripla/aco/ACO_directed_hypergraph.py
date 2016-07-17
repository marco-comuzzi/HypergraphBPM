'''
Created on Jun 16, 2016

@author: UNIST
'''

from halp.directed_hypergraph import DirectedHypergraph 
from org.emettelatripla.aco.ACO_util import *
from org.emettelatripla.util.util import *


# node_set: the source node set (only one node in process models)
# hg: the process model (hypergraph)
#ANT_NUM number of ants in one colony
#COL_NUM number of colonies
#tau: pheromone evaporation coefficient 
def aco_algorithm(node_set, hg, ANT_NUM, COL_NUM, tau):
    #currently optimal path
    p_opt = DirectedHypergraph()
    utility_opt = 0.0
    #counters for colony
    col = 0
    while col < COL_NUM:
        #counter for ant number
        ant = 0
        print("Processing colony n. "+str(col))
        #h_graph to store partial pheromone update
        hg_phero = hg.copy()
        #do something
        p = DirectedHypergraph()
        #add source node to optimal path (and its attributes)
        for node in node_set:
            p.add_node(node, hg.get_node_attributes(node))
        while ant < ANT_NUM:
            print("--- Processing ant n. "+str(ant))
            #call aco_search on p
            p = aco_search(p, hg, node_set)
            print_hg(p,'hyp_file.txt')
            #calculate utility of p
            utility = calculate_utility(p)
            #calculate partial pheromone update
            partial_phero_update(hg_phero, p)
            #check if p is better than current optimal solution
            #update if p is optimal
            print("Utility of current path: "+str(utility)+" (opt utility: "+str(utility_opt)+")")
            if utility > utility_opt:
                utility_opt = utility
                p_opt = p
                print("optimal path updated!")
            ant = ant + 1
            #pheromone update
            #TBC TBC
        col = col + 1
        #actual pheromone update
        final_phero_update(hg, p_opt, tau)
    #do something else
    print("********** OPTIMAL PATH FOUND ******************")
    print_hg(p_opt, 'hyp_file.txt')
    print("UTILITY: "+str(calculate_utility(p_opt)))
    print("***********************************************")

#node_set: current position (can be a set of nodes) in the search
#p: current path
#hg: process model
def aco_search(p, hg, node_set):
    #select next hyperedge from node according to pheromone distribution
    edge_set = set()
    for node in node_set:
        edge_set = set.union(edge_set,hg.get_forward_star(node))
    #select edge based on value of pheromone attribute (and add h_edge to current solution
    next_edge = phero_choice(edge_set, hg)
    tail = hg.get_hyperedge_tail(next_edge)
    head = hg.get_hyperedge_head(next_edge)
    attrs = hg.get_hyperedge_attributes(next_edge)
    print_hyperedge(next_edge, hg)
    #add selected hyperedge/node to p
    p.add_hyperedge(tail, head, attrs)
    next_head = hg.get_hyperedge_head(next_edge)
    for node in next_head:
        p.add_node(node, hg.get_node_attributes(node))
    #must add also all nodes in the tail (i fnot already)
    next_tail = hg.get_hyperedge_tail(next_edge)
    for node in next_tail:
        p.add_node(node, hg.get_node_attributes(node))
    #if new node added is sink, then return p
    isSink = False
    for node in next_head:
        if hg.get_node_attribute(node,'sink') == True:
            isSink = True
    if isSink == False:
        aco_search(p, hg, next_head)
    #else recursive call
    return p