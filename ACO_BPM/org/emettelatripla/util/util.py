'''
Created on Jun 16, 2016

@author: UNIST
'''
from halp.directed_hypergraph import DirectedHypergraph
import logging

def print_hg(hg, file_name):
    #logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', filename='C://BPMNexamples/aco.log',level=logging.INFO)
    logger = logging.getLogger(__name__)
    hg.write(file_name, ',','\t')
    logger.debug("========= Printing hypergraph... =============================")
    f = open(file_name, 'r')
    contents = f.readlines()
    #for i in contents:
    #    print(i)
    f.close()
    for node in hg.get_node_set():
        print_node(node, hg)
    for edge in hg.get_hyperedge_id_set():
        print_hyperedge(edge, hg)
    logger.debug("========== Printing hypergraph complete ======================")
    
def print_hg_std_out_only(hg):
    #hg.write(file_name, ',','\t')
    logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', filename='C://BPMNexamples/aco.log',level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.debug("========= Printing hypergraph... =============================")
    for node in hg.get_node_set():
        print_node(node, hg, logger)
    for edge in hg.get_hyperedge_id_set():
        print_hyperedge(edge, hg, logger)
    logger.debug("========== Printing hypergraph complete ======================")
    
def print_node(node, hg):
    logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', filename='C://BPMNexamples/aco.log',level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.debug("Node: {0} ### Attributes: {1}".format(str(node), hg.get_node_attributes(node)))
    
def print_hyperedge(h_edge, hg):
    logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', filename='C://BPMNexamples/aco.log',level=logging.INFO)
    logger = logging.getLogger(__name__)
    h_edge_name = str(hg.get_hyperedge_attribute(h_edge,'name'))
    h_edge_tail = str(hg.get_hyperedge_tail(h_edge))
    h_edge_head = str(hg.get_hyperedge_head(h_edge))
    h_edge_phero = str(hg.get_hyperedge_attribute(h_edge, 'phero'))
    #h_edge_id = str(hg.get_hyperedge_attribute(h_edge, 'id'))
    logger.debug("Hyperedge: {0} ### Tail: {1} ### Head: {2} ### Phero: {3}".format(str(h_edge), h_edge_tail, h_edge_head, h_edge_phero))