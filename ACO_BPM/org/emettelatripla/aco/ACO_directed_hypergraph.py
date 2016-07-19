'''
Created on Jun 16, 2016

@author: UNIST
'''

import logging
from halp.directed_hypergraph import DirectedHypergraph 
from org.emettelatripla.aco.ACO_util import *
from org.emettelatripla.util.util import *

#setup logger



# node_set: the source node set (only one node in process models)
# hg: the process model (hypergraph)
#ANT_NUM number of ants in one colony
#COL_NUM number of colonies
#tau: pheromone evaporation coefficient 
#W_UTILITY: weights of the utility function
def aco_algorithm(start_node_set, hg, ANT_NUM, COL_NUM, tau, W_UTILITY):
    #set the values of the utility function weights
    W_COST = W_UTILITY['cost']
    W_AVAIL = W_UTILITY['avail']
    W_QUAL = W_UTILITY['qual']
    W_TIME = W_UTILITY['time']
    #setup the logger
    #logging.basicConfig(filename='aco.log',level=logging.INFO)
    logger = logging.getLogger(__name__)
    #currently optimal path
    p_opt = DirectedHypergraph()
    utility_opt = 0.0
    #counters for colony
    col = 0
    while col < COL_NUM:
        #counter for ant number
        ant = 0
        logger.info("Processing COLONY n. {0}".format(col))
        #h_graph to store partial pheromone update
        hg_phero = hg.copy()
        #do something
        p = DirectedHypergraph()
        #add source node to optimal path (and its attributes)
        for node in start_node_set:
            p.add_node(node, hg.get_node_attributes(node))
        while ant < ANT_NUM:
            logger.info("--- Processing COLONY n. {1}, ANT n. {0}".format(ant, col))
            p = DirectedHypergraph()
            #add source node to optimal path (and its attributes)
            for node in start_node_set:
                p.add_node(node, hg.get_node_attributes(node))
            #call aco_search on p
            p = aco_search(p, hg, start_node_set)
            #PRINT CURRENT OPTIMAL PATH
            print_hg(p,'hyp_file.txt')
            #calculate utility of p
            utility = calculate_utility(p, W_COST, W_TIME, W_QUAL, W_AVAIL)
            #do partial pheromone update
            partial_phero_update(hg_phero, p, W_COST, W_TIME, W_QUAL, W_AVAIL)
            #check if p is better than current optimal solution
            #update if p is optimal
            logger.debug("Utility of current path: {0} ".format(utility))
            logger.debug("Current OPTIMAL UTILITY: {0}".format(utility_opt))
            if utility > utility_opt:
                utility_opt = utility
                p_opt = p
                logger.info("***** optimal path updated!!! *****")
            ant = ant + 1
            #pheromone update
            #TBC TBC
        col = col + 1
        #actual pheromone update after processing an entire colony
        final_phero_update(hg, p_opt, tau)
    #do something else
    logger.info("********** OPTIMAL PATH FOUND ******************")
    print_hg(p_opt, 'hyp_file.txt')
    logger.info("****** UTILITY: "+str(calculate_utility(p_opt, W_COST, W_TIME, W_QUAL, W_AVAIL)))
    logger.info("***********************************************")
    return p_opt

#start_node_set: current position (can be a set of nodes) in the search
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
    #get the id of the next_edge and use it as id of new edge in p
    id = next_edge
    attrs.update({'id' : id})
    #add selected hyperedge/node to p
    if p.has_hyperedge(tail, head):
        i=0
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