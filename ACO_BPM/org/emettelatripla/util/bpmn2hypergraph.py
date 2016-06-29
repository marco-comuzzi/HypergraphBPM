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

# # Open XML document using minidom parser
file_name = "C://example.bpmn"
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


#convert a bpmn diagram into an hypergraph
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
            convertTask(start, hyperg, bpmndiagram)
    printHgStdOutOnly(hyperg)
    return hyperg

def convertTask(task, hyperg, bpmndiagram):
    ns = {'bpmn':'http://www.omg.org/spec/BPMN/20100524/MODEL' }
    out_flows = bpmndiagram.findall("./bpmn:process/bpmn:sequenceFlow[@sourceRef='"+task.attrib['id']+"']", ns)
    for out_flow in out_flows:
        print("New outgoing arc found: "+str(out_flow.attrib['id']))
        #find target nodes
        targets = bpmndiagram.findall("./bpmn:process/*[@id='"+out_flow.attrib['targetRef']+"']", ns)
        for target in targets:
            print("-- New Target found! : "+str(target.attrib['name']))
            #if target is task: add hyperdge and recursively call on target task
            #if target is XOR: add hyperedge and recursively call on target task
            #if target is AND: add hyperdge and call on all targets



#flow = "node_05c888e8-2ebe-4d1b-a838-29d032d8ebda"
#print(str(isFlowInGateway(flow, bpmndiagram)))

convertBpmnToProcessHgraph(file_name)
