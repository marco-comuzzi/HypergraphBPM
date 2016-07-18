'''
Created on Jun 16, 2016

@author: UNIST
'''
from halp.directed_hypergraph import DirectedHypergraph
from org.emettelatripla.util.util import *
from org.emettelatripla.aco.ACO_directed_hypergraph import *
from org.emettelatripla.aco.ACO_util import *
import logging

# Initialize an empty hypergraph
H = DirectedHypergraph()

# Add nodes 's' and 't' individually with arbitrary attributes
H.add_node('A', sink=False, source=True, cost=0.245, avail=0.99, qual=0.7, time=0.78)
H.add_node('B', sink=False, source=False, cost=0.245, avail=0.99, qual=0.7, time=0.78)
H.add_node('C', sink=False, source=False, cost=0.245, avail=0.99, qual=0.7, time=0.78)
H.add_node('D', sink=False, source=False, cost=0.245, avail=0.99, qual=0.7, time=0.78)
H.add_node('E', sink=False, source=False, cost=0.245, avail=0.99, qual=0.7, time=0.78)
H.add_node('G', sink=False, source=False, cost=0.245, avail=0.99, qual=0.7, time=0.78)
H.add_node('H', sink=False, source=False, cost=0.245, avail=0.99, qual=0.7, time=0.78)
H.add_node('F', source=False, sink=True, cost=0.1, avail=0.98, qual=0.4, time=0.45)

hyperedges = [(['A'], ['B'], {'name' : " ", 'phero': 0.3}),
              (['A'], ['D','E'], {'name' : " ", 'phero': 0.1}),
              (['A'], ['G'], {'name' : " ", 'phero': 0.6}),
              (['B'], ['C'], {'name' : " ", 'phero': 0.0}),
              (['D','E'], ['F'], {'name' : " ", 'phero': 0.0}),
              (['E','H'], ['F'], {'name' : " ", 'phero': 0.0}),
              (['G'], ['H'], {'name' : " ", 'phero': 0.0}),
              (['H'], ['F'], {'name' : " ", 'phero': 0.0}),
              (['C'], ['F'], {'name' : " ", 'phero': 0.0})  
        ]
H.add_hyperedges(hyperedges)

#edges = H.get_forward_star('A')
# for edge in edges:
#     printHyperedge(edge, H)
# print("Choosing hyperedge.....")
# printHyperedge(pheroChoice(edges, H), H)

aco_algorithm(['A'], H, 5, 5, 0.77)

