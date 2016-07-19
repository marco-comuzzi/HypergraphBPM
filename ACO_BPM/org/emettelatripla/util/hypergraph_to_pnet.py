'''
Created on Jul 18, 2016

The main idea here is, given the initial Petri net, to delete what is not in the optimal hyperpath

Quick & dirty: find all transitions that are not in the optimal path and remove them, together with all the arcs
having them as source or targets

@author: UNIST
'''

from halp import directed_hypergraph
from org.emettelatripla.util.pnet_to_hypergraph import get_transitions
import xml.etree.ElementTree as ET

def get_transitions_from_opt_path(hg_opt):
    """ returns the list of names of transition in the hypergraph (excluding xor splits and joins)"""
    nodes = hg_opt.get_node_set()
    transitions = []
    for node in nodes:
        if hg_opt.get_node_attribute(node, 'type') == 'transition':
            transitions.append(hg_opt.get_node_attribute(node, 'name'))
    return transitions

def get_pnet_from_file(file_name):
    """ returns a pnet xml object of the file in file_name"""
    tree = ET.parse(file_name)
    pnet = tree.getroot()
    return pnet

def get_transitions_from_pnet(pnet):
    transitions = get_transitions(pnet)
    return transitions


def convert_path_to_pnet(pnet_file_name, hg_opt):
    #get pnet xml object
    pnet = get_pnet_from_file(pnet_file_name)
    #get transitions from pnet
    t_set_pnet = get_transitions_from_pnet(pnet)
    #get transition list from optimal path
    t_set_opt = get_transitions_from_pnet(hg_opt)
    #REMOVE TRANSITIONS FROM PNET
    #REMOVE ARCS FROM PNET
    #CHECK PLACES OF PNET
    #REWRITE PNET


def main():
    file_name = "something"
    pnet = get_pnet_from_file(file_name)

if __name__ == '__main__':
    main