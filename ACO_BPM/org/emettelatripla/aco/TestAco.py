'''
Created on Jun 16, 2016

@author: UNIST
'''
from directed_hypergraph import DirectedHypergraph
from org.emettelatripla.util.util import *
from org.emettelatripla.aco.ACODirectedHypergraph import *

# Initialize an empty hypergraph
H = DirectedHypergraph()

# Add nodes 's' and 't' individually with arbitrary attributes
H.add_node('A', sink=False, source=True, cost=0.245, avail=0.99, qual=0.7, time=0.78, phero=0.0)
H.add_node('B', sink=False, source=False, cost=0.245, avail=0.99, qual=0.7, time=0.78, phero=0.0)
H.add_node('C', sink=False, source=False, cost=0.245, avail=0.99, qual=0.7, time=0.78, phero=0.0)
H.add_node('D', sink=False, source=False, cost=0.245, avail=0.99, qual=0.7, time=0.78, phero=0.0)
H.add_node('E', sink=False, source=False, cost=0.245, avail=0.99, qual=0.7, time=0.78, phero=0.0)
H.add_node('G', sink=False, source=False, cost=0.245, avail=0.99, qual=0.7, time=0.78, phero=0.0)
H.add_node('H', sink=False, source=False, cost=0.245, avail=0.99, qual=0.7, time=0.78, phero=0.0)
H.add_node('F', source=False, sink=True, cost=0.1, avail=0.98, qual=0.4, time=0.45, phero=0.0)

hyperedges = [(['A'], ['B'], {'weight': 2}),
              (['A'], ['D','E'], {'weight': 100}),
              (['A'], ['G'], {'weight': 1}),
              (['B'], ['C'], {'weight': 3}),
              (['D','E'], ['F'], {'weight': 3}),
              (['E','H'], ['F'], {'weight': 3}),
              (['G'], ['H'], {'weight': 3}),
              (['H'], ['F'], {'weight': 3}),
              (['C'], ['F'], {'weight': 3})  
        ]
H.add_hyperedges(hyperedges)

acoAlgorithm(['A'], H, 5, 4, 0.78)

