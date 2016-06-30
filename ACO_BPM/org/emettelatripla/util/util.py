'''
Created on Jun 16, 2016

@author: UNIST
'''
from directed_hypergraph import DirectedHypergraph

def printHg(hg:DirectedHypergraph, file_name):
    hg.write(file_name, ',','\t')
    print("========= Printing hypergraph... =============================")
    f = open(file_name, 'r')
    contents = f.readlines()
    #for i in contents:
     #   print(i)
    f.close()
    for node in hg.get_node_set():
        printNode(node, hg)
    for edge in hg.get_hyperedge_id_set():
        printHyperedge(edge, hg)
    print("========== Printing hypergraph complete ======================")
    
def printHgStdOutOnly(hg:DirectedHypergraph):
    #hg.write(file_name, ',','\t')
    print("========= Printing hypergraph... =============================")
    #f = open(file_name, 'r')
    #contents = f.readlines()
    #for i in contents:
     #   print(i)
    #f.close()
    for node in hg.get_node_set():
        printNode(node, hg)
    for edge in hg.get_hyperedge_id_set():
        printHyperedge(edge, hg)
    print("========== Printing hypergraph complete ======================")
    
def printNode(node, hg:DirectedHypergraph):
    print("Found new node: "+str(node)+" ++ "+str(hg.get_node_attributes(node)))
    
def printHyperedge(h_edge, hg:DirectedHypergraph):
    print("Hyperedge: TAIL: "+str(hg.get_hyperedge_tail(h_edge))+" ++ HEAD: "+str(hg.get_hyperedge_head(h_edge))+" ++ phero: "+str(hg.get_hyperedge_attribute(h_edge, 'phero')))