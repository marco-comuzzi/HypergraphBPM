'''
Created on Jul 18, 2016

@author: UNIST
'''
import logging
import xml.etree.ElementTree as ET
from halp.directed_hypergraph import DirectedHypergraph
from org.emettelatripla.util.pnet_to_hypergraph import convert_pnet_to_hypergraph
from org.emettelatripla.aco.ACO_util import random_init_attributes,\
    reduce_opt_path_pnet
from org.emettelatripla.aco.ACO_util import show_opt_path_pnet
from org.emettelatripla.aco.ACO_directed_hypergraph import aco_algorithm
from org.emettelatripla.util.util import print_node, print_hg
#from org.emettelatripla.util.bpmn_to_hypergraph import file_name
import sys

def main():
    #setup the logger
    logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', filename='C://BPMNexamples/aco.log',level=logging.DEBUG)
    logger = logging.getLogger(__name__)
    
    print(str(sys.getrecursionlimit()))
    sys.setrecursionlimit(100000000)
    print(str(sys.getrecursionlimit()))
    
    
    #file_name = "C://BPMNexamples/inductive/ex1_inductive.pnml"
    #file_name = "C://BPMNexamples/inductive/ex4_inductive.pnml"
    #file_name = "C://BPMNexamples/real_logs/hospital_inductive.pnml"
    #file_name = "C://BPMNexamples/inductive/repair_start_end_inductive.pnml"
    #file_name = "C://BPMNexamples/inductive/ex6_claim_inductive.pnml"
    #The following has loop:
    #file_name = "C://BPMNexamples/inductive/ex5_review_inductive.pnml"
    #file_name = "C://BPMNexamples/alpha/ex1_alpha.pnml"
    
    #MINED WITH INDUCTIVE MINER
    #file_root = "ex1_inductive"
    file_root = "bpi_challenge2012"
    #file_root = "road_fine_process"
    file_type = "inductive"
    
    #MINED WITH ALPHA MINER
    #file_root = "ex6_claim_alpha"
    #file_type = "alpha"
    
    file_name = "C://BPMNexamples/"+file_type+"/"+file_root+".pnml"
    
    tree = ET.parse(file_name)
    pnet = tree.getroot()
    
    hg = DirectedHypergraph()
    #convert pnet into hypergraph
    hg = convert_pnet_to_hypergraph(pnet)
    
    
    #randomly initialise hypergraph
    hg = random_init_attributes(hg)
    print_hg(hg,'hyp.txt')
    
    #find start node (MAKE A FUNCTION FOR IT!!!!)
    nodes = hg.get_node_set()
    start_nodes = []
    for node in nodes:
        if hg.get_node_attribute(node, 'source') == True:
            logger.debug("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
            logger.debug("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
            logger.debug("Found start node: {0}".format(print_node(node, hg)))
            logger.debug("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
            logger.debug("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
            start_nodes.append(node)
    
    #run ACO optimisation
    tau = 0.6
    ANT_NUM = 10
    COL_NUM = 3
    W_UTILITY = {'cost' : 1.0, 'avail' : 0.0, 'qual' : 0.0, 'time' : 0.0}
    
    #call ACO algorithm
    p_opt = aco_algorithm(start_nodes, hg, ANT_NUM, COL_NUM, tau, W_UTILITY)
    
    #highlight on pnet
    show_opt_path_pnet(p_opt, tree, file_root)
    
    #reduce
    reduce_opt_path_pnet(tree, file_root)
    
    


if __name__ == "__main__":
    main()