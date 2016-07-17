'''
Created on Jul 13, 2016

@author: UNIST
'''


import graphspace_interface.graphspace_interface as interface
import networkx as nx
import random
import sys


def upload_graphspace(user,password,group,G,graphid,outfile):
    

    interface.validate_json(G)
    interface.postGraph(G,graphid,outfile=outfile,user=user,password=password,logfile='tmp.log')
    if group != None:
        interface.shareGraph(graphid,user=user,password=password,group=group)
    return

    

def runExample2(user,password,group,graphid,outfile):
    #############
    ## Graph 2 (tmp2): randomly generate nodes and edges.

    G = nx.DiGraph(directed=True)
    # add 10 nodes
    nodeids = ['node\n%d' % (i) for i in range(10)]
    for n in nodeids:
        interface.add_node(G,n,label=n,bubble='yellow',color='yellow')
    for i in range(20): # randomly add 20 edges
        interface.add_edge(G,random.choice(nodeids),random.choice(nodeids),width=random.choice([1,2,3,4,5]),directed=True)

    interface.validate_json(G)
    interface.postGraph(G,graphid,outfile=outfile,user=user,password=password,logfile='tmp.log')
    if group != None:
        interface.shareGraph(graphid,user=user,password=password,group=group)
    return