'''
Created on Jun 16, 2016

@author: UNIST
'''
from halp.directed_hypergraph import DirectedHypergraph
from org.emettelatripla.util.util import *
from collections import OrderedDict
import random
import operator
from random import uniform
import logging
import xml.etree.ElementTree as ET
from org.emettelatripla.util.pnet_to_hypergraph import get_transitions,\
    get_transition_name
import sys


def partial_phero_update(hg_phero, p, w_cost, w_time, w_qual, w_avail):
    #update the phero level of all nodes in p
    #logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', filename='C://BPMNexamples/aco.log',level=logging.INFO)
    logger = logging.getLogger(__name__)
    p_edge_set = p.get_hyperedge_id_set()
    p_utility = calculate_utility(p, w_cost, w_time, w_qual, w_avail)
    #for now, utility is the cost
    for p_edge in p_edge_set:
        p_edge_id = p.get_hyperedge_attribute(p_edge, 'id')
        curr_phero = hg_phero.get_hyperedge_attribute(p_edge_id, 'phero')
        p.add_hyperedge(p.get_hyperedge_tail(p_edge), p.get_hyperedge_head(p_edge), phero = curr_phero + p_utility, id = p_edge_id)
        logger.debug("Partial phero update - Phero value: {0}".format(str(p.get_hyperedge_attribute(p_edge, 'phero'))))
        logger.debug("Partial phero update - id: {0}".format(str(p.get_hyperedge_attribute(p_edge, 'id'))))
       
#tau is the evaporation coefficient
def final_phero_update(hg, hg_partial, tau):
    edge_set = hg_partial.get_hyperedge_id_set()
    for edge in edge_set:
        edge_id = hg_partial.get_hyperedge_attribute(edge, 'id')
        #evaporate current phero on hg and add partial update from hg_partial
        evap_u = tau * hg.get_hyperedge_attribute(edge_id, 'phero')
        new_phero = evap_u + hg_partial.get_hyperedge_attribute(edge, 'phero')
        hg.add_hyperedge(hg_partial.get_hyperedge_tail(edge), hg_partial.get_hyperedge_head(edge), phero = new_phero, id = edge_id)
    
    
#must be parameterised with weoghts    
def calculate_utility(hg, w_cost, w_time, w_qual, w_avail):
    utility = 0.0
    utility = (w_cost * calc_utility_cost(hg)) + (w_time * calc_utility_time(hg)) + (w_qual * calc_utility_qual(hg)) + (w_avail * calc_utility_avail(hg))
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
    #setup the logger
    #logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', filename='C://BPMNexamples/aco.log',level=logging.INFO)
    logger = logging.getLogger(__name__)
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
    choice = random.uniform(0, high)
    #logger.debug("Random number to choose next edge: {0} ==== Cumulative choice list: {1}".format(str(choice),str(cumul_hash)))
    #logger.debug("Sorted dict: {0}".format(str(sorted_dict)))
    #logger.debug("Hash pheroval: {0}".format(str(hash_pheroval)))
    #logger.debug("Hash edge_id: {0}".format(str(hash_edgeid)))
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
        elif choice <= cumul_hash[0]:
            notFound = False
            edge_in = 0
        elif choice > cumul_hash[i] and choice <= cumul_hash[i+1]:
            notFound = False
            edge_in = i+1
        i = i+1
    #calculate chosen edge
    #print("Chosen edge i: "+str(i))
    chosen_edge = hash_edgeid[edge_in] 
    logger.debug("^^^ Edge selected based on pheromone choice: {0}".format(str(chosen_edge)))
    #print_hyperedge(chosen_edge, hg)
    #logger.debug("^^^ end selected hyperedge print ^^^^")
    return chosen_edge

def random_init_attributes(hg):
    """ Initialise the attributes cost, qual, avail, and time of a hypergraph
    to random values drawn from a uniform distribution [0,1]"""
    nodes = hg.get_node_set()
    for node in nodes:
        cost = uniform(0,1)
        qual = uniform(0,1)
        avail = uniform(0,1)
        time = uniform(0,1)
        attrs = hg.get_node_attributes(node)
        #hg.remove_node(node)
        attrs.update({'cost' : cost})
        attrs.update({'qual' : qual})
        attrs.update({'avail' : avail})
        attrs.update({'time' : time})
        hg.add_node(node, attrs)
    return hg

def get_transitions_from_opt_path(hg_opt):
    """ returns the list of names of transition in the hypergraph (excluding xor splits and joins)"""
    nodes = hg_opt.get_node_set()
    transitions = []
    for node in nodes:
        if hg_opt.get_node_attribute(node, 'type') == 'transition':
            transitions.append(hg_opt.get_node_attribute(node, 'name'))
    return transitions

def show_opt_path_pnet(hg_opt, tree, file_root):
    """ given optimal path (hypergraph hg_opt) and a Petri net (tree), it highlights the optimal path in the Petri net
    (highlihgting the non xor/tau nodes in the Petri net 
    This functions also "re-colors" the tau-split and joins in the pnet"""
    logger = logging.getLogger(__name__)
    #get the list of nodes
    pnet = tree.getroot()
    #nodes = get_transitions_from_opt_path(hg_opt)
    nodes = hg_opt.get_node_set()
    #color
    red_color = ET.Element('fill', color = '#c30e2d')
    grey_color = ET.Element('fill', color = '#A9A9A9')
    #for each node, add fill color in pnet
    trans_pnet = get_transitions(pnet)
    
        #find node in pnet
    for t_pnet in trans_pnet:
        t_name = t_pnet.find("./name/text").text
        in_opt_path = False
        for node in nodes:
            if  t_name == node:
                in_opt_path = True
                logger.debug("Transition {0} is in the optimal path - Node: {1}".format(t_name,node))
        if in_opt_path:
            if t_name[0:3] == 'tau':
                logger.debug("Found tau transition on optimal path: making it visible...")
                t_pnet.find('./toolspecific').attrib['activity'] = t_name
            #node found, add red_color as element
            logger.debug("Colouring red - node: {0} ...".format(t_name))
            graphics = t_pnet.find('graphics')
            #graphics = t_children.Element('graphics')
            graphics.append(red_color)
        #adjust tau split and tau join
#         else:
#             if node[:2] == 'tau':
#                 logger.debug("Found tau transition outside optimal path found: making it visible and grey...")
#                 # make it visible
#                 t_pnet.find('./toolspecific').attrib['activity'] = node
#                 # change colour
#                 graphics = t_pnet.find('graphics')
#                 graphics.append(grey_color)
    output_file = "C://BPMNexamples/output/"+file_root+"_highlight.pnml"
    logger.debug("writing output on file: {0}".format(output_file))
    tree.write(output_file, encoding='utf-8')
    
def reduce_opt_path_pnet(tree, file_root):
    """ given a pnet with highlighted optimal path, it deletes all the non relevant detail from the pnet"""
    logger = logging.getLogger(__name__)
    logger.debug("Reducing pnet...")
    pnet = tree.getroot()
    #STEP 1: delete not highlighted transitions
    #trans_pnet = get_transitions(pnet)
    trans_pnet = pnet.findall('.net/page/transition')
    page = pnet.findall('.net/page')
    for t_pnet in trans_pnet:
        graphics = t_pnet.find('graphics')
        fills = graphics.findall('fill')
        delete = True
        for fill in fills:
            if fill.attrib['color'] == '#c30e2d':
                delete = False
        if delete:
            #remove transition
            logger.debug("Found transitions to remove (reduce): {0}".format(get_transition_name(t_pnet)))
            #t2s = pnet.findall('.net/page/transition')
            t_name = get_transition_name(t_pnet)
            page = pnet.find('./net/page')
            #find arcs to remove
            t_id = t_pnet.get('id')
            arcs = pnet.findall('./net/page/arc')
            for arc in arcs:
                if arc.get('source') == t_id or arc.get('target') == t_id:
                    page.remove(arc)
            #remove transition
            page.remove(t_pnet)      
    #STEP 2: delete arcs sourcing from or targeting non highlighted transitions and places
    # TO BE COMPLETED
    #write the output
    tree.write("C://BPMNexamples/output/"+file_root+"_reduced.pnml", encoding='utf-8')
        
        
        