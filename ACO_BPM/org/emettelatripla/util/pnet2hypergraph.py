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
from org.emettelatripla.aco.ACOUtil import *
from org.emettelatripla.util.util import *
from networkx.classes.digraph import DiGraph
from networkx.classes.digraph import Graph

#setup the logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

file_name = "C://BPMNexamples/review.pnml"

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


    

# =====================
# Some useful functions to process pnml
# ====================
def get_places(pnet):
    return pnet.findall("./net/page/place")

def get_transitions(pnet):
    return pnet.findall("./net/page/transition")

def get_arcs(pnet):
    return pnet.findall("./net/page/arc")

def get_transition_name(t):
    return t.find("./name/text").text

def get_id(element):
    return element.attrib['id']

def get_arc_source(arc):
    return arc.attrib['source']

def get_arc_target(arc):
    return arc.attrib['target']

def get_incoming_arcs(transition):
    t_id = get_id(transition)
    inc_arcs = pnet.findall("./net/page/arc[@target='"+t_id+"']")
    return inc_arcs

def get_outgoing_arcs(transition):
    t_id = get_id(transition)
    inc_arcs = pnet.findall("./net/page/arc[@source='"+t_id+"']")
    return inc_arcs

#============================

#Main procedure to convert pnet in hypergraph
def convert_pnet_to_hypergraph(pnet):
    hg = DirectedHypergraph()
    #scan all transitions and create hyperedges
    transitions = get_transitions(pnet)
    for transition in transitions:
        #get all incoming arcs, the source of these become the tail of hyperedge
        inc_arcs = get_incoming_arcs(transition)
        tail = []
        for inc_arc in inc_arcs:
            source = str(get_arc_source(inc_arc))
            tail.append(source)
        #get all outgoing arcs, the target of these become the head of the hyperedge
        out_arcs = get_outgoing_arcs(transition)
        head = []
        for out_arc in out_arcs:
            target = str(get_arc_target(out_arc))
            head.append(target)
        name = get_transition_name(transition)
        hg.add_hyperedge(tail, head, name = name, phero = 0.0, cost = 0.4, avail = 0.6, qual = 0.2, time = 0.99)
    #print the result before exit
    print_hg_std_out_only(hg)
    return hg

hg = convert_pnet_to_hypergraph(pnet)

#convert hypergaph to directed graph
dg = DiGraph()
dg = to_networkx_digraph(hg)
#draw diected graph
nx.draw(dg)
plt.show()

