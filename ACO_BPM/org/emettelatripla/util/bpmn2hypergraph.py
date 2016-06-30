'''
Created on 2016. 6. 29.

@author: UNIST
'''

#from xml.dom.minidom import parse
#import xml.dom.minidom
import xml.etree.ElementTree as ET
from directed_hypergraph import DirectedHypergraph
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
def convertBpmnToProcessHgraph(bpmn_file_name):
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
            #logger.info(getTag(start))
            visited = []
            hyperg = inspectTask(start, hyperg, bpmndiagram, [])
    printHgStdOutOnly(hyperg)
    return hyperg


def inspectTask(node, hyperg, bpmndiagram, visited):
    ns = {'bpmn':'http://www.omg.org/spec/BPMN/20100524/MODEL' }
    #if end event: stop
    if getTag(node) == 'endEvent':
        visited.append(node)
        logger.info("Visiting END EVENT")
    #if AND split/join do not process and move to target node
    elif getTag(node) == 'parallelGateway':
        logger.info("Visiting PARALLEL gateway: "+getId(node))
        outgoings = getOutgoingFlows(node, bpmndiagram)
        for outgoing in outgoings:
            node = getTargetRef(outgoing, bpmndiagram)
            if visited.count(node) == 0:
                visited.append(node)
                inspectTask(node, hyperg, bpmndiagram, visited)
    elif getTag(node) == 'startEvent' or getTag(node) == 'task' or getTag(node) == "exclusiveGateway":
        logger.info("Visiting Element: "+getId(node)+" NAME: "+getName(node))
        outgoings = getOutgoingFlows(node, bpmndiagram)
        #find all outgoings to task or xor join/split
        task_outgoings = []
        for outgoing in outgoings:
            if getTag(getTargetRef(outgoing, bpmndiagram)) == 'task' or getTag(getTargetRef(outgoing, bpmndiagram)) == 'exclusiveGateway':
                task_outgoings.append(getTargetRef(outgoing, bpmndiagram))
        #add hyperedge in hypergraph
        #build tail
        tail_hyper = []
        tail_hyper.append(getId(node))
        #add node explicitly
        addNodeInHypergraph(node, hyperg)
        #build head
        head_hyper = []
        for outgoing in outgoings:
            head_hyper.append(getId(getTargetRef(outgoing, bpmndiagram)))
            addNodeInHypergraph(getTargetRef(outgoing, bpmndiagram), hyperg)
        #add hyperdge
        addEdgeInHypergraph(tail_hyper, head_hyper, hyperg)
        #still traversing the process, not sure if needed!!!!
        for outgoing in outgoings:
            node = getTargetRef(outgoing, bpmndiagram)
            if visited.count(node) == 0:
                visited.append(node)
                inspectTask(node, hyperg, bpmndiagram, visited)
    return hyperg

def addNodeInHypergraph(node, hyperg):
    hyperg.add_node(getId(node), name = getName(node), sink = False, source = False, cost = 0.1, qual = 0.6, avail = 0.9, time = 0.2)

def addEdgeInHypergraph(tail, head, hyperg):
    for node in tail:
        if not hyperg.has_node(node):
            logging.warning("This node is not in graph: "+str(node))
    for node in head:
        if not hyperg.has_node(node):
            logging.warning("This node is not in graph: "+str(node))
    hyperg.add_hyperedge(tail, head, phero=0.4)       

#a simple traversal algorithm
def bpmnDiagramTraversal(node, hyperg, bpmndiagram, visited):
    ns = {'bpmn':'http://www.omg.org/spec/BPMN/20100524/MODEL' }
    #if end event: stop
    if getTag(node) == 'endEvent':
        visited.append(node)
        logger.info("END EVENT found!!!")
    #if AND split/join do not process and move to target node
    elif getTag(node) == 'parallelGateway':
        logger.info("Visiting PARALLEL gateway: "+getId(node))
        outgoings = getOutgoingFlows(node, bpmndiagram)
        for outgoing in outgoings:
            node = getTargetRef(outgoing, bpmndiagram)
            if visited.count(node) == 0:
                visited.append(node)
                bpmnDiagramTraversal(node, hyperg, bpmndiagram, visited)
    elif getTag(node) == 'startEvent' or getTag(node) == 'task' or getTag(node) == "exclusiveGateway":
        logger.info("Visiting Element: "+getId(node)+" NAME: "+getName(node))
        outgoings = getOutgoingFlows(node, bpmndiagram)
        for outgoing in outgoings:
            node = getTargetRef(outgoing, bpmndiagram)
            if visited.count(node) == 0:
                visited.append(node)
                bpmnDiagramTraversal(node, hyperg, bpmndiagram, visited)
    return hyperg

            


    
#BPMN: given SequenceFlow >> id of the target element
def getTargetRef(flow, bpmndiagram):
    ns = {'bpmn':'http://www.omg.org/spec/BPMN/20100524/MODEL' }
    element_id = flow.attrib['targetRef']
    element = bpmndiagram.find("./bpmn:process/*[@id='"+element_id+"']", ns)
    return element

#BPMN: given SequenceFlow >> id of the source element
def getSourceRef(flow, bpmnDiagram):
    ns = {'bpmn':'http://www.omg.org/spec/BPMN/20100524/MODEL' }
    element_id = flow.attrib['sourceRef']
    element = bpmndiagram.find("./bpmn:process/*[@id='"+element_id+"']", ns)
    return element
    
#BPMN: given Element >> get list of of id of outgoing sequence flows
def getOutgoingFlows(element, bpmndiagram):
    ns = {'bpmn':'http://www.omg.org/spec/BPMN/20100524/MODEL' }
    out_flows = bpmndiagram.findall("./bpmn:process/bpmn:sequenceFlow[@sourceRef='"+element.attrib['id']+"']", ns)
    return out_flows

#BPMN: given Element >> get list of of id of incoming sequence flows
def getIncomingFlows(element, bpmndiagram):
    ns = {'bpmn':'http://www.omg.org/spec/BPMN/20100524/MODEL' }
    out_flows = bpmndiagram.findall("./bpmn:process/bpmn:sequenceFlow[@targetRef='"+element.attrib['id']+"']", ns)
    return out_flows
    

def getId(element):
    if 'id' in element.keys():
        return element.attrib['id']
    else:
        return element.text

def getName(element):
    return element.attrib['name']

def getText(element):
    return element.text

def getTag(element):
    prefix = '{http://www.omg.org/spec/BPMN/20100524/MODEL}'
    return element.tag[len(prefix):]


tree = ET.parse(file_name)
bpmndiagram = tree.getroot()
#get info from startEvent
ns = {'bpmn':'http://www.omg.org/spec/BPMN/20100524/MODEL' }
# starts = bpmndiagram.findall("./bpmn:process/bpmn:task", ns)
# for start in starts:
#     logger.info("===== Found START event...")
#     print("ID: "+str(getId(start)))
#     print("Name: "+str(getName(start)))
#     outflows = getOutgoingFlows(start, bpmndiagram)
#     for flow in outflows:
#         print("Outgoing flow: "+getId(flow))
#         logger.info(">> Target ref: "+str(getTargetRef(flow, bpmndiagram)))
#     print("===========================")
#      
# xorgateways = bpmndiagram.findall("./bpmn:process/bpmn:exclusiveGateway", ns)
# andgateways = bpmndiagram.findall("./bpmn:process/bpmn:parallelGateway", ns)
#  
# gateways = list(set(xorgateways).union(andgateways))
# for gateway in gateways:
#     print("+++++ Found new gateway....")
#     print("ID: "+str(getId(gateway)))
#     outgoings = getOutgoingFlows(gateway, bpmndiagram)
#     incomings = getIncomingFlows(gateway, bpmndiagram)
#     for incoming in incomings:
#         print("Incoming flow: "+getId(incoming))
#     for outgoing in outgoings:
#         print("Outgoing flow: "+getId(outgoing))
#     print("+++++++++++++++++++++++++++")

    

    

convertBpmnToProcessHgraph(file_name)
