'''
Created on 2016. 6. 29.

@author: UNIST
'''

#from xml.dom.minidom import parse
#import xml.dom.minidom
import xml.etree.ElementTree as ET
from halp.directed_hypergraph import DirectedHypergraph
from org.emettelatripla.aco.ACOUtil import *
from org.emettelatripla.util.util import *
import logging

#setup the logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# # Open XML document using minidom parser
file_name = "C://BPMNexamples/simplexor.bpmn"



# tree = ET.parse(file_name)
# bpmndiagram = tree.getroot()
# print(bpmndiagram.tag)
# ns = {'bpmn':'http://www.omg.org/spec/BPMN/20100524/MODEL' }
# 
# # Get all the movies in the collection
# tasks = bpmndiagram.findall("./bpmn:process/bpmn:task", ns)
# for task in tasks:
#     name = task.attrib['name']
#     print ("New task found: "+name)
# processes = bpmndiagram.findall("bpmn:process", ns)
# for process in processes:
#     print ("Process id : "+process.attrib['id'])


#convert a bpmn diagram into an hypergraph: MAIN PROCEDURE
def convert_bpmn_to_process_hgraph(bpmn_file_name):
    hyperg = DirectedHypergraph();
    #namespace
    ns = {'bpmn':'http://www.omg.org/spec/BPMN/20100524/MODEL' }
    #parse bpmn file
    tree = ET.parse(file_name)
    bpmndiagram = tree.getroot()
    #parse process
    processes = bpmndiagram.findall("./bpmn:process", ns)
    for process in processes:
        #pick start event
        starts = bpmndiagram.findall("./bpmn:process/bpmn:startEvent", ns)
        for start in starts:
            hyperg.add_node(start.attrib['id'], name=start.attrib['name'], cost=0.1, qual=0.1, avail=0.1, time=0.1)
            #logger.info(get_tag(start))
            visited = []
            hyperg = inspect_task(start, hyperg, bpmndiagram, [])
    print_hg_std_out_only(hyperg)
    return hyperg


def inspect_task(node, hyperg, bpmndiagram, visited):
    ns = {'bpmn':'http://www.omg.org/spec/BPMN/20100524/MODEL' }
    #if end event: stop
    if get_tag(node) == 'endEvent':
        visited.append(node)
        logger.info("Visiting END EVENT")
    #if AND split/join do not process and move to target node
    elif get_tag(node) == 'parallelGateway':
        logger.info("Visiting PARALLEL gateway: "+get_id(node))
        outgoings = get_outgoing_flows(node, bpmndiagram)
        for outgoing in outgoings:
            node = get_target_ref(outgoing, bpmndiagram)
            if visited.count(node) == 0:
                visited.append(node)
                inspect_task(node, hyperg, bpmndiagram, visited)
    elif get_tag(node) == 'startEvent' or get_tag(node) == 'task' or get_tag(node) == "exclusiveGateway":
        logger.info("Visiting Element: "+get_id(node)+" NAME: "+get_name(node))
        outgoings = get_outgoing_flows(node, bpmndiagram)
        #find all outgoings to task or xor join/split
        task_outgoings = []
        for outgoing in outgoings:
            if get_tag(get_target_ref(outgoing, bpmndiagram)) == 'task' or get_tag(get_target_ref(outgoing, bpmndiagram)) == 'exclusiveGateway':
                task_outgoings.append(get_target_ref(outgoing, bpmndiagram))
        #add hyperedge in hypergraph
        #build tail
        tail_hyper = []
        tail_hyper.append(get_id(node))
        #add node explicitly
        add_node_in_hypergraph(node, hyperg)
        #build head
        head_hyper = []
        for outgoing in outgoings:
            head_hyper.append(get_id(get_target_ref(outgoing, bpmndiagram)))
            add_node_in_hypergraph(get_target_ref(outgoing, bpmndiagram), hyperg)
        #add hyperdge
        add_edge_in_hypergraph(tail_hyper, head_hyper, hyperg)
        #still traversing the process, not sure if needed!!!!
        for outgoing in outgoings:
            node = get_target_ref(outgoing, bpmndiagram)
            if visited.count(node) == 0:
                visited.append(node)
                inspect_task(node, hyperg, bpmndiagram, visited)
    return hyperg

def add_node_in_hypergraph(node, hyperg):
    hyperg.add_node(get_id(node), name = get_name(node), sink = False, source = False, cost = 0.1, qual = 0.6, avail = 0.9, time = 0.2)

def add_edge_in_hypergraph(tail, head, hyperg):
    for node in tail:
        if not hyperg.has_node(node):
            logging.warning("This node is not in graph: "+str(node))
    for node in head:
        if not hyperg.has_node(node):
            logging.warning("This node is not in graph: "+str(node))
    hyperg.add_hyperedge(tail, head, phero=0.4)       

#a simple traversal algorithm
def bpmn_diagram_traversal(node, hyperg, bpmndiagram, visited):
    ns = {'bpmn':'http://www.omg.org/spec/BPMN/20100524/MODEL' }
    #if end event: stop
    if get_tag(node) == 'endEvent':
        visited.append(node)
        logger.info("END EVENT found!!!")
    #if AND split/join do not process and move to target node
    elif get_tag(node) == 'parallelGateway':
        logger.info("Visiting PARALLEL gateway: "+get_id(node))
        outgoings = get_outgoing_flows(node, bpmndiagram)
        for outgoing in outgoings:
            node = get_target_ref(outgoing, bpmndiagram)
            if visited.count(node) == 0:
                visited.append(node)
                bpmn_diagram_traversal(node, hyperg, bpmndiagram, visited)
    elif get_tag(node) == 'startEvent' or get_tag(node) == 'task' or get_tag(node) == "exclusiveGateway":
        logger.info("Visiting Element: "+get_id(node)+" NAME: "+get_name(node))
        outgoings = get_outgoing_flows(node, bpmndiagram)
        for outgoing in outgoings:
            node = get_target_ref(outgoing, bpmndiagram)
            if visited.count(node) == 0:
                visited.append(node)
                bpmn_diagram_traversal(node, hyperg, bpmndiagram, visited)
    return hyperg

            


    
#BPMN: given SequenceFlow >> id of the target element
def get_target_ref(flow, bpmndiagram):
    ns = {'bpmn':'http://www.omg.org/spec/BPMN/20100524/MODEL' }
    element_id = flow.attrib['targetRef']
    element = bpmndiagram.find("./bpmn:process/*[@id='"+element_id+"']", ns)
    return element

#BPMN: given SequenceFlow >> id of the source element
def get_source_ref(flow, bpmnDiagram):
    ns = {'bpmn':'http://www.omg.org/spec/BPMN/20100524/MODEL' }
    element_id = flow.attrib['sourceRef']
    element = bpmndiagram.find("./bpmn:process/*[@id='"+element_id+"']", ns)
    return element
    
#BPMN: given Element >> get list of of id of outgoing sequence flows
def get_outgoing_flows(element, bpmndiagram):
    ns = {'bpmn':'http://www.omg.org/spec/BPMN/20100524/MODEL' }
    out_flows = bpmndiagram.findall("./bpmn:process/bpmn:sequenceFlow[@sourceRef='"+element.attrib['id']+"']", ns)
    return out_flows

#BPMN: given Element >> get list of of id of incoming sequence flows
def get_incoming_flows(element, bpmndiagram):
    ns = {'bpmn':'http://www.omg.org/spec/BPMN/20100524/MODEL' }
    out_flows = bpmndiagram.findall("./bpmn:process/bpmn:sequenceFlow[@targetRef='"+element.attrib['id']+"']", ns)
    return out_flows
    

def get_id(element):
    if 'id' in element.keys():
        return element.attrib['id']
    else:
        return element.text

def get_name(element):
    return element.attrib['name']

def get_text(element):
    return element.text

def get_tag(element):
    prefix = '{http://www.omg.org/spec/BPMN/20100524/MODEL}'
    return element.tag[len(prefix):]


tree = ET.parse(file_name)
bpmndiagram = tree.getroot()
#get info from startEvent
ns = {'bpmn':'http://www.omg.org/spec/BPMN/20100524/MODEL' }
# starts = bpmndiagram.findall("./bpmn:process/bpmn:task", ns)
# for start in starts:
#     logger.info("===== Found START event...")
#     print("ID: "+str(get_id(start)))
#     print("Name: "+str(get_name(start)))
#     outflows = get_outgoing_flows(start, bpmndiagram)
#     for flow in outflows:
#         print("Outgoing flow: "+get_id(flow))
#         logger.info(">> Target ref: "+str(get_target_ref(flow, bpmndiagram)))
#     print("===========================")
#      
# xorgateways = bpmndiagram.findall("./bpmn:process/bpmn:exclusiveGateway", ns)
# andgateways = bpmndiagram.findall("./bpmn:process/bpmn:parallelGateway", ns)
#  
# gateways = list(set(xorgateways).union(andgateways))
# for gateway in gateways:
#     print("+++++ Found new gateway....")
#     print("ID: "+str(get_id(gateway)))
#     outgoings = get_outgoing_flows(gateway, bpmndiagram)
#     incomings = get_incoming_flows(gateway, bpmndiagram)
#     for incoming in incomings:
#         print("Incoming flow: "+get_id(incoming))
#     for outgoing in outgoings:
#         print("Outgoing flow: "+get_id(outgoing))
#     print("+++++++++++++++++++++++++++")

    

    

convert_bpmn_to_process_hgraph(file_name)
