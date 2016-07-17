'''
Created on Jun 16, 2016

@author: UNIST
'''
from halp.directed_hypergraph import DirectedHypergraph
from org.emettelatripla.util.util import *
from org.emettelatripla.aco import ACO_util
from org.emettelatripla.aco.ACO_util import calc_utility_avail
from org.emettelatripla.aco.ACO_util import calc_utility_cost
from org.emettelatripla.aco.ACO_util import calc_utility_time
from org.emettelatripla.aco.ACO_util import calc_utility_qual


# Initialize an empty hypergraph
H = DirectedHypergraph()

# Add nodes 's' and 't' individually with arbitrary attributes
H.add_node('A', sink=False, source=True, cost=0.245, avail=0.99, qual=0.7, time=0.75, phero=0.0)
H.add_node('B', sink=False, source=False, cost=0.645, avail=0.92, qual=0.7, time=0.79, phero=0.0)
H.add_node('C', sink=False, source=False, cost=0.745, avail=0.69, qual=0.7, time=0.98, phero=0.0)
H.add_node('D', sink=False, source=False, cost=0.845, avail=0.99, qual=0.5, time=0.28, phero=0.0)
H.add_node('E', sink=False, source=False, cost=0.445, avail=0.99, qual=0.3, time=0.48, phero=0.0)
H.add_node('G', sink=False, source=False, cost=0.545, avail=0.99, qual=0.7, time=0.98, phero=0.0)
H.add_node('H', sink=False, source=False, cost=0.245, avail=0.99, qual=0.7, time=0.68, phero=0.0)
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

#printHg(H, 'hyp_file.txt')

#nodes = H.get_node_set()
#for node in nodes:
#     printNode(node, H)
#     
# edges = H.get_hyperedge_id_set()
# for id in edges:
#     printHyperedge(id, H)
    
calc_utility_avail(H)
#Test utility function
print("Utility COST: "+str(calc_utility_cost(H)))
print("Utility AVAIL: "+str(calc_utility_avail(H)))
print("Utility QUAL: "+str(calc_utility_qual(H)))
print("Utility TIME: "+str(calc_utility_time(H)))
#print("Utility: "+str())
