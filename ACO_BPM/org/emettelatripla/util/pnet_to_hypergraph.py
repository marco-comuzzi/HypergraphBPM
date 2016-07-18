'''
Created on Jul 6, 201

Translates Petri net into Hypergraph
Works with PNML Petri nets extracted from ProM

@author: UNIST
'''
import logging
import xml.etree.ElementTree as ET
from halp.directed_hypergraph import DirectedHypergraph
from halp.utilities.directed_graph_transformations import to_networkx_digraph
import matplotlib.pyplot as plt
import networkx as nx
from org.emettelatripla.aco.ACO_util import *
from org.emettelatripla.util.util import *
from networkx.classes.digraph import DiGraph
from networkx.classes.digraph import Graph
from org.emettelatripla.util import util
from org.emettelatripla.util.graph_space_interface import upload_graphspace
from org.emettelatripla.aco.ACO_util import random_init_attributes

#setup the logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


    

# =====================
# Some useful functions to process pnml
# ====================

def get_element(id, pnet):
    return pnet.find("./net/page/*[@id='"+id+"']")

def get_places(pnet):
    return pnet.findall("./net/page/place")

def get_transitions(pnet):
    return pnet.findall("./net/page/transition")

def get_arcs(pnet):
    return pnet.findall("./net/page/arc")

def get_transition_name(t):
    return t.find("./name/text").text

def set_transition_name(t, name):
    t.find("./name/text").text = name

def get_id(element):
    return element.attrib['id']

def get_arc_source(arc):
    return arc.attrib['source']

def get_arc_target(arc):
    return arc.attrib['target']

def get_incoming_arcs(element, pnet):
    t_id = get_id(element)
    inc_arcs = pnet.findall("./net/page/arc[@target='"+t_id+"']")
    return inc_arcs

def get_outgoing_arcs(element, pnet):
    t_id = get_id(element)
    inc_arcs = pnet.findall("./net/page/arc[@source='"+t_id+"']")
    return inc_arcs


#============================

#Main procedure to convert pnet in hypergraph
#This works only if there are no xor split/join in the Petri net!!!
def convert_pnet_to_hypergraph_andgatewayonly(pnet):
    hg = DirectedHypergraph()
    #scan all transitions and create hyperedges
    transitions = get_transitions(pnet)
    for transition in transitions:
        #get all incoming arcs, the source of these become the tail of hyperedge
        inc_arcs = get_incoming_arcs(transition,pnet)
        tail = []
        for inc_arc in inc_arcs:
            source = str(get_arc_source(inc_arc))
            tail.append(source)
        #get all outgoing arcs, the target of these become the head of the hyperedge
        out_arcs = get_outgoing_arcs(transition,pnet)
        head = []
        for out_arc in out_arcs:
            target = str(get_arc_target(out_arc))
            head.append(target)
        name = get_transition_name(transition)
        hg.add_hyperedge(tail, head, name = name, phero = 0.0, cost = 0.4, avail = 0.6, qual = 0.2, time = 0.99)
    #print the result before exit
    print_hg_std_out_only(hg)
    return hg

def tau_pre_processing_pnet(pnet):
    """ Assign progressive numbers to tau-split and tau-join transitions (to manage multiple occurrence)"""
    logger.info("Pre processing tau-split-join transitions...")
    transitions = get_transitions(pnet)
    i = 0
    j = 0
    for transition in transitions:
        if get_transition_name(transition) == 'tau split':
            logger.info("Pre processing, updating tau-split transition: {0}".format(get_transition_name(transition)))
            set_transition_name(transition, 'tau split'+str(i))
            i = i+1
        if get_transition_name(transition) == 'tau join':
            logger.info("Pre processing, updating tau-join transition: {0}".format(get_transition_name(transition)))
            set_transition_name(transition, 'tau join'+str(j))
            j = j+1

def tau_post_processing(hg):
    """ POST-PROCESSING of tau-split, tau-join nodes (in pnets created from inductive miner"""
    # tau-from-tree nodes don't have to be processed?
    # TO BE COMPLETED
    # TO BE COMPLETED
    nodes = hg.get_node_set()
    for node in nodes:
        node_name = hg.get_node_attribute(node, 'name')
        if node_name[:8] == 'tau join':
            #getbackward star
            b_star = hg.get_backward_star(node)
            #get tails of backward star h_edges
            tails = []
            for edge in b_star:
                tails = list(set(tails).union(hg.get_hyperedge_tail(edge)))
                hg.remove_hyperedge(edge)
            #create new h_edge
            head = []
            head.append(node)
            hg.add_hyperedge(tails, head, name = " ", phero = 0.0, cost = 0.4, avail = 0.6, qual = 0.2, time = 0.99)
        node_name = hg.get_node_attribute(node, 'name')
        if node_name[:9] == 'tau split':
            #get forward star
            f_star = hg.get_forward_star(node)
            heads = []
            for edge in f_star:
                heads = list(set(heads).union(hg.get_hyperedge_head(edge)))
                hg.remove_hyperedge(edge)
            #create new h_edge
            tail = []
            tail.append(node)
            hg.add_hyperedge(tail, heads, name = " ", phero = 0.0, cost = 0.4, avail = 0.6, qual = 0.2, time = 0.99)
    return hg

def tau_reduction(hg):
    """ reduces a hypergraph by deleting the tau-split/join nodes"""
    nodes = hg.get_node_set()
    for node in nodes:
        node_name = hg.get_node_attribute(node, 'name')
        """ Reduce tau splits """
        if node_name[:9] == 'tau split' or node_name[:8] == 'tau join':
            logger.info("Found new tau transition to reduce: {0}".format(node_name))
            #get forward star and build head for new hyperedge
            f_star = hg.get_forward_star(node)
            new_head = []
            for edge in f_star:
                new_head = list(set(new_head).union(hg.get_hyperedge_head(edge)))
            #remove current hyperedge
            hg.remove_hyperedge(edge)
            #get backward star and build tail of new hyperedge
            b_star = hg.get_backward_star(node)
            new_tail = []
            for edge in b_star:
                new_tail = list(set(new_tail).union(hg.get_hyperedge_tail(edge)))
            hg.remove_hyperedge(edge)
            #create new hyperedge
            hg.add_hyperedge(new_tail, new_head, name = " ", phero = 0.0, cost = 0.4, avail = 0.6, qual = 0.2, time = 0.99)
    return hg

def convert_pnet_to_hypergraph(pnet):
    """ pre-process pnet to number tau-split and tau-join transitions"""
    tau_pre_processing_pnet(pnet)
    """ Convert a Petri net (in pnml format) into a hypergraph (Halp format) """
    hg = DirectedHypergraph()
    transitions = get_transitions(pnet)
    places = get_places(pnet)
    """STEP 1: Pre-process places to find xor places (splits and joints)
    If input/output of a transitions is 2 or more places, then mark those places as "X" and put in hypergraph"""
    for place in places:
        inc_arcs = get_incoming_arcs(place,pnet)
        out_arcs = get_outgoing_arcs(place,pnet)
        isSink = False
        isSource = False
        if len(inc_arcs) > 1:
            #create node for place in hypergraph
            node_id = get_id(place)
            #check if join is end event (sink)
            if (len(out_arcs) == 0):
                isSink = True
            logger.info("STEP 1 - Creating xor-join node -- {0}".format(node_id))
            hg.add_node(node_id, source = isSource, sink = isSink, type = 'xor-join', name = " ")
            head = []
            head.append(node_id)
            isSink = False
            isSource = False
            #create node for all source of incoming arcs
            for arc in inc_arcs:
                node_id2 = get_id(get_element(get_arc_source(arc), pnet))
                node_name = get_transition_name(get_element(get_arc_source(arc), pnet))
                logger.info("STEP 1 - Creating transition node -- {0} -- {1}".format(node_id, node_name))
                hg.add_node(node_name, source = isSource, sink = isSink, type = 'transition', name = node_name)
                tail = []
                tail.append(node_name)
                #create hyperedge
                logger.info("STEP 1 - Creating hyperedge from {0} to {1}".format(str(tail), str(head)))
                hg.add_hyperedge(tail, head, name = " ", phero = 0.0, cost = 0.4, avail = 0.6, qual = 0.2, time = 0.99)
        if len(out_arcs) > 1:
            node_id = get_id(place)
            #create node for place in hypergraph (if it does not exist already)
            tail = []
            tail.append(node_id)
            if(not hg.has_node(node_id)):
                #check if source (start event)
                if (len(inc_arcs) == 0):
                    isSource = True
                logger.info("STEP 1 - Creating xor-split node -- {0}".format(node_id))
                hg.add_node(node_id, source = isSource, sink = isSink, type = 'xor-split', name = " ")
                #create node for all targets of outgoing arcs
                isSink = False
                isSource = False
                for arc in out_arcs:
                    node_id2 = get_id(get_element(get_arc_target(arc), pnet))
                    node_name = get_transition_name(get_element(get_arc_target(arc),pnet))
                    if(not hg.has_node(node_id2)):
                        logger.info("STEP 1 - Creating transition node -- {0} -- {1}".format(node_id, node_name))
                        hg.add_node(node_name, source = isSource, sink = isSink, type = 'transition', name = node_name)
                    head = []
                    head.append(node_name)
                    #create hyperedge
                    logger.info("STEP 1 - Creating hyperedge from {0} to {1}".format(str(tail), str(head)))
                    hg.add_hyperedge(tail, head, name = " ", phero = 0.0, cost = 0.4, avail = 0.6, qual = 0.2, time = 0.99)
    """ STEP2 : Process each transition """
    for transition in transitions:
        logger.info("######## Processing transition {0}".format(get_transition_name(transition)))
        isSink = False
        isSource = False
        #check if transition is not a node in hg and add if needed
        #if (not hg.has_node(get_transition_name(transition))):
        #check if transition is start
        inc_arcs = get_incoming_arcs(transition,pnet)
        for inc_arc in inc_arcs:
            source_place = get_element(get_arc_source(inc_arc),pnet)
            place_inc = get_incoming_arcs(source_place,pnet)
            if not place_inc:
                isSource = True
                logger.info("Transition is START: {0}".format(get_transition_name(transition)))
        #check if trsnasition is end event
        out_arcs = get_outgoing_arcs(transition,pnet)
        for out_arc in out_arcs:
            sink_place = get_element(get_arc_target(out_arc),pnet)
            place_out = get_outgoing_arcs(sink_place,pnet)
            if not place_out:
                isSink = True
                logger.info("Transition is END: {0}".format(get_transition_name(transition)))
        #create node in hypergraph
        logger.info("STEP 2 - Creating transition node")
        hg.add_node(get_transition_name(transition), source = isSource, sink = isSink, type = 'transition', name = get_transition_name(transition))
        #look BACKWARD 
        if not isSource:
            inc_arcs = get_incoming_arcs(transition,pnet)
            tail = []
            x_head = [get_transition_name(transition)]
            xplace_list = []
            otherp_list = []
            xplace_tail = []
            for inc_arc in inc_arcs:
                place = get_element(get_arc_source(inc_arc),pnet)
                #separate xor places from other forward places of this transition
                if(hg.has_node(get_id(place))):
                    xplace_list.append(place)
                    xplace_tail.append(get_id(place))
                else:
                    otherp_list.append(place)
                #create forward hyperedge to possibly multiple xor nodes
            he_from_xors_needed = False
            for place in xplace_tail:
                temp_tail = []
                temp_tail.append(place)
                if(not hg.has_hyperedge(temp_tail,x_head)):
                    he_from_xors_needed = True
            if(he_from_xors_needed):    
                logger.info("STEP 2 - Creating backward hyperedge to (multiple) xor - TAIL {0} -- HEAD {1} ".format(str(xplace_tail),str(x_head)))
                hg.add_hyperedge(xplace_tail, x_head, name = " ", phero = 0.0, cost = 0.4, avail = 0.6, qual = 0.2, time = 0.99)
                #create forward normal hyperdge
            tail = []
#             for place in otherp_list:
#                 inc_arcs_l2 = get_incoming_arcs(place)
#                 for inc_arc_l2 in inc_arcs_l2:
#                     trans2 = get_element(get_arc_source(inc_arc_l2))
#                     tail.append(get_transition_name(trans2))
#             if(tail):
#                 logger.info("STEP 2 - Creating real backward  hyperedge - TAIL {0} -- HEAD {1} ".format(str(tail),str(x_head)))
#                 hg.add_hyperedge(tail, x_head, name = " ", phero = 0.0, cost = 0.4, avail = 0.6, qual = 0.2, time = 0.99)
        #look FORWARD
        if not isSink:
            out_arcs = get_outgoing_arcs(transition,pnet)
            head = []
            x_tail = [get_transition_name(transition)]
            xplace_list = []
            otherp_list = []
            xplace_head = []
            for out_arc in out_arcs:
                place = get_element(get_arc_target(out_arc),pnet)
                #separate xor places from other forward places of this transition
                if(hg.has_node(get_id(place))):
                    xplace_list.append(place)
                    xplace_head.append(get_id(place))
                else:
                    otherp_list.append(place)
                #create forward hyperedge to possibly multiple xor nodes
            he_to_xors_needed = False
            for place in xplace_head:
                temp_head = []
                temp_head.append(place)
                if(not hg.has_hyperedge(x_tail,temp_head)):
                    he_to_xors_needed = True
            if(he_to_xors_needed):
                logger.info("STEP 2 - Creating forward hyperedge to (multiple) xor - TAIL {0} -- HEAD {1} ".format(str(x_tail),str(xplace_head)))
                hg.add_hyperedge(x_tail, xplace_head, name = " ", phero = 0.0, cost = 0.4, avail = 0.6, qual = 0.2, time = 0.99)
                #create forward normal hyperdge
            head = []
            for place in otherp_list:
                out_arcs_l2 = get_outgoing_arcs(place,pnet)
                for out_arc_l2 in out_arcs_l2:
                    trans2 = get_element(get_arc_target(out_arc_l2),pnet)
                    head.append(get_transition_name(trans2))
            if(head):
                logger.info("STEP 2 - Creating real forward  hyperedge - TAIL {0} -- HEAD {1} ".format(str(x_tail),str(head)))
                hg.add_hyperedge(x_tail, head, name = " ", phero = 0.0, cost = 0.4, avail = 0.6, qual = 0.2, time = 0.99)
    ## POST PROCESSING of tau-split/join generated by inductive miner
    hg = tau_post_processing(hg)
    #reduction of tau splits and joins
    hg = tau_reduction(hg)
    return hg

def number_of_start_events(hg):
    nodes = hg.get_node_set()
    i = 0
    for node in nodes:
        is_source = hg.get_node_attribute(node, 'source')
        if is_source:
            i = i+1
    return i
    
    
def number_of_end_events(hg):
    nodes = hg.get_node_set()
    i = 0
    for node in nodes:
        is_source = hg.get_node_attribute(node, 'sink')
        if is_source:
            i = i+1
    return i

def number_of_xor_splits(hg):
    """ returns number of xor-splits"""
    return get_statistics(hg)['xor-split']

def number_of_xor_joints(hg):
    """ returns number of xor-joints"""
    return get_statistics(hg)['xor-join']

def number_of_activities(hg):
    """ returns number of activities (ie. number of transitions excluding xor splits and joins)"""
    return get_statistics(hg)['activities']

def number_of_transitions(hg):
    """returns total number of transitions (including xor splits/joins)"""
    return get_statistics(hg)['transitions']

def get_statistics(hg):
    """ returns some basic statistics of the hypergraph in a dictionary"""
    stats = {}
    xor_splits = 0
    xor_joins = 0
    total_trans = 0
    activities = 0
    nodes = hg.get_node_set()
    for node in nodes:
        total_trans = total_trans + 1
        node_type = hg.get_node_attribute(node,'type')
        if node_type == "xor-split":
            xor_splits = xor_splits + 1
        elif node_type == "xor-join":
            xor_joins = xor_joins + 1
        else:
            activities = activities + 1
            
    stats.update({'xor-split' : xor_splits})
    stats.update({'xor-join' : xor_joins})
    stats.update({'activities' : activities})
    stats.update({'transitions' : total_trans})
    return stats

def print_statistics(hg):
    print(str(get_statistics(hg)))
    
    
def main():
    
    
    file_name = "C://BPMNexamples/inductive/ex4_inductive.pnml"
    #file_name = "C://BPMNexamples/real_logs/hospital_inductive.pnml"
    
    tree = ET.parse(file_name)
    pnet = tree.getroot()
    
    print(pnet.tag)
    
    # places = pnet.findall("./net/page/place")
    # 
    # for place in places:
    #     logger.info("Found new place: "+str(place.attrib['id']))
    #     
    transitions = pnet.findall("./net/page/transition")
    # 
    for transition in transitions:
        name = transition.find("./name/text").text
        logger.info("Found new Transition: "+str(transition.attrib['id'])+" NAME: "+name)
         
    # arcs = pnet.findall("./net/page/arc")
    # 
    # for arc in arcs:
    #     id = str(arc.attrib['id'])
    #     source = str(arc.attrib['source'])
    #     target = str(arc.attrib['target'])
    #     logger.info("Found new arc --- ID: "+id+" SOURCE: "+source+" TARGET: "+target)
    
    hg = convert_pnet_to_hypergraph(pnet)
    print_hg(hg, "hyp_file.txt")
    logger.info("Number of start events: {0}".format(number_of_start_events(hg)))
    logger.info("Number of end events: {0}".format(number_of_end_events(hg)))
    print_statistics(hg)

#hg = random_init_attributes(hg)
#print_hg(hg, "hyp_file.txt")



#hg = convert_pnet_to_hypergraph_andgatewayonly(pnet)
#print_hg(hg, "hyp_file.txt")

#convert hypergaph to directed graph
#dg = DiGraph()
#dg = to_networkx_digraph(hg)
#draw diected graph
#nx.draw(dg)
#plt.show()

#Upload to graphspace (doesn't work, but it prints json that can be uploaded :)
#upload_graphspace("mcomuzzi@unist.ac.kr", "Uniqlo4321", "test", dg, "test001", "hyp_file.json")
    
if __name__ == "__main__":
    main()





