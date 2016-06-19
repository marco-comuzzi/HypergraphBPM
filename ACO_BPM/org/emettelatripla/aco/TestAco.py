'''
Created on Jun 16, 2016

@author: UNIST
'''
from directed_hypergraph import DirectedHypergraph
from org.emettelatripla.util.util import *
from org.emettelatripla.aco.ACODirectedHypergraph import *
from org.emettelatripla.aco.ACOUtil import *

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

hyperedges = [(['A'], ['B'], {'phero': 0.3}),
              (['A'], ['D','E'], {'phero': 0.1}),
              (['A'], ['G'], {'phero': 0.6}),
              (['B'], ['C'], {'phero': 0.0}),
              (['D','E'], ['F'], {'phero': 0.0}),
              (['E','H'], ['F'], {'phero': 0.0}),
              (['G'], ['H'], {'phero': 0.0}),
              (['H'], ['F'], {'phero': 0.0}),
              (['C'], ['F'], {'phero': 0.0})  
        ]
H.add_hyperedges(hyperedges)

#edges = H.get_forward_star('A')
# for edge in edges:
#     printHyperedge(edge, H)
# print("Choosing hyperedge.....")
# printHyperedge(pheroChoice(edges, H), H)

acoAlgorithm(['A'], H, 2, 2, 0.77)

