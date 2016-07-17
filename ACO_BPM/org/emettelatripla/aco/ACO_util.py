'''
Created on Jun 16, 2016

@author: UNIST
'''
from halp.directed_hypergraph import DirectedHypergraph
from org.emettelatripla.util.util import *
from collections import OrderedDict
import random
import operator


def partial_phero_update(hg_phero, p):
    #update the phero level of all nodes in p
    p_edge_set = p.get_hyperedge_id_set()
    p_utility = calculate_utility(p)
    #for now, utility is the cost
    for p_edge in p_edge_set:
        curr_phero = hg_phero.get_hyperedge_attribute(p_edge, 'phero')
        p.add_hyperedge(p.get_hyperedge_tail(p_edge), p.get_hyperedge_head(p_edge), phero = curr_phero + p_utility)
        print("Phero value: "+str(p.get_hyperedge_attribute(p_edge, 'phero')))
       
#tau is the evaporation coefficient
def final_phero_update(hg, hg_partial, tau):
    edge_set = hg_partial.get_hyperedge_id_set()
    for edge in edge_set:
        #evaporate current phero on hg and add partial update from hg_partial
        evap_u = tau * hg.get_hyperedge_attribute(edge, 'phero')
        new_phero = evap_u + hg_partial.get_hyperedge_attribute(edge, 'phero')
        hg.add_hyperedge(hg_partial.get_hyperedge_tail(edge), hg_partial.get_hyperedge_head(edge), phero = new_phero)
    
    
#must be parameterised with weoghts    
def calculate_utility(hg, w_cost, w_time, w_qual, w_avail):
    utility = 0.0
    utility = (w_cost * calculate_utility(hg)) + (w_time * calc_utility_time(hg)) + (w_qual * calc_utility_qual(hg)) + (w_avail * calc_utility_avail(hg))
    return utility

#this simply calculates utility as sum of cost
def calculate_utility_test(hg):
    utility = 0.0
    node_set = hg.get_node_set()
    for node in node_set:
        print_node(node, hg)
        utility = utility + hg.get_node_attribute(node,'cost')
    return utility

#this works for any anti-additive utility measure (just change the get_node_attribute)
def calc_utility_cost(p):
    node_set = p.get_node_set()
    #calculate number of nodes in node_set
    node_num = len(node_set)
    #calculate sum of costs of all nodes
    total_cost = 0
    for node in node_set:
        total_cost = total_cost + p.get_node_attribute(node, 'cost')
    #calculate utility
    utility = 1 - (total_cost / node_num)
    return utility

def calc_utility_time(p):
    return 0

def calc_utility_qual(p):
    node_set = p.get_node_set()
    #create list to have ordered elements
    node_list = list(node_set)
    #calculate number of nodes in node_set
    node_num = len(node_list) 
    #initialise utility value
    utility = p.get_node_attribute(node_list[0], 'qual')
    #calculate minimum of quality of nodes in path
    i = 0
    while i < node_num:
        curr_utility = p.get_node_attribute(node_list[i], 'qual')
        if curr_utility < utility:
            utility = curr_utility
        i = i + 1
    #calculate utility
    return utility

def calc_utility_avail(p):
    node_set = p.get_node_set()
    #calculate number of nodes in node_set
    node_num = len(node_set)
    #calculate product of avail for all nodes
    total_cost = 1.0
    for node in node_set:
        total_cost = total_cost * p.get_node_attribute(node, 'avail')
    #calculate utility
    utility = total_cost
    return utility

        
#debugged!
def phero_choice(edge_set, hg):
    #create an ordered list of tuples (edge_id, phero_value)
    dic = {}
    for edge in edge_set:
        dic[edge] = hg.get_hyperedge_attribute(edge, 'phero')
    sorted_dict = sorted(dic.items(), key=operator.itemgetter(1))
    #build hash_pheroval like [edge_id]>[phero value]
    hash_pheroval = [item[1] for item in sorted_dict]
    hash_edgeid = [item[0] for item in sorted_dict]
#     for edge in edge_set:
#         hash_pheroval.append(hg.get_hyperedge_attribute(edge, 'phero'))
#         hash_edgeid.append(edge)
    # build cumulative hash_pheroval to compare randomly extracted variable
    cumul_hash = list(hash_pheroval)
    i=0
    while i < len(hash_pheroval):
        j = 0
        while j < i:
            cumul_hash[i] = cumul_hash[i] + hash_pheroval[j]
            j = j+1
        i = i+1
    #print("This is the list: "+str(hash_pheroval))
    #print("This is the cumul list: "+str(cumul_hash))
    #extract random number and check
    len_ch = len(cumul_hash)-1
    low = cumul_hash[0]
    high = cumul_hash[len_ch]
    choice = random.uniform(low, high)
    print("Random number is: "+str(choice))
    #caculate the edge_id based on the drawn random number
    notFound = True
    i = 0
    edge_in = 0
    while (notFound):
        #adjust if only 1 edge available (or if chosen is last edge in the list)
        if i == (len(cumul_hash) - 1):
            notFound = False
            edge_in = i
        #general case
        elif choice <= cumul_hash[i+1]:
            notFound = False
            edge_in = i
        i = i+1
    #calculate chosen edge
    #print("Chosen edge i: "+str(i))
    chosen_edge = hash_edgeid[edge_in] 
    print("^^^ Edge selected based on pheromone choice: ")
    print_hyperedge(chosen_edge, hg)
    print("^^^ end selected hyperedge print ^^^^")
    return chosen_edge