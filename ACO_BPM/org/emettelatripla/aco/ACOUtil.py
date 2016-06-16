'''
Created on Jun 16, 2016

@author: UNIST
'''
from directed_hypergraph import DirectedHypergraph
from org.emettelatripla.util.util import *


def partialPheroUpdate(hg_phero:DirectedHypergraph, p:DirectedHypergraph):
    #update the phero level of all nodes in p
    p_node_set = p.get_node_set()
    #for now, utility is the cost
    for p_node in p_node_set:
        p_utility = p.get_node_attribute(p_node, 'cost')
        hg_phero_utility = hg_phero.get_node_attribute(p_node, 'phero')
        new_phero = p_utility + hg_phero_utility
        hg_phero.add_node(p_node, phero = new_phero)
        print("Phero value: "+str(new_phero))
       
#tau is the evaporation coefficient
def finalPheroUpdate(hgPhero:DirectedHypergraph, hg_partial:DirectedHypergraph, tau):
    node_set = hg_partial.get_node_set()
    for node in node_set:
        #evaporate current phero on hgPhero and add partial update from hg_partial
        evap_u = tau * hgPhero.get_node_attribute(node, 'phero')
        new_phero = evap_u + hg_partial.get_node_attribute(node, 'phero')
        hgPhero.add_node(node, phero = new_phero)
        
def calculateUtility(hg:DirectedHypergraph):
    utility = 0.0
    node_set = hg.get_node_set()
    for node in node_set:
        printNode(node, hg)
        utility = utility + hg.get_node_attribute(node,'cost')
    return utility
        
#this choice function simply picks the edge with highest weight
def pheroChoice(edge_set, hg:DirectedHypergraph):
    max = 0
    max_edge = ()
    for edge in edge_set:
        if hg.get_hyperedge_attribute(edge,'weight') > max:
            max = hg.get_hyperedge_attribute(edge,'weight')
            max_edge = edge
    print("^^^ Edge selected based on pheromone choice: ")
    printHyperedge(max_edge, hg)
    return max_edge