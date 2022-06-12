from __future__ import annotations

import logging
import argparse
import tempfile
import os
from lxml import etree
from lxml.etree import Element, ElementTree, QName

# Shared Use-Case RDF/XML elements
RDF_NS = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'
RDF_NS_LXML = '{%s}' % RDF_NS  
CIM_NS = 'http://iec.ch/TC57/CIM100#'
CIM_NS_LXML =  '{%s}' % CIM_NS
RDF_ABOUT = '%s%s' % (RDF_NS_LXML, "about")
RDF_RESOURCE = '%s%s' % (RDF_NS_LXML, "resource")


# A dictionary that contains literal property names whose integer values need to be
# modified by a multiplier.
# KEY: integer multiplier VALUE: list of property names
# TODO Replace with data-driven approach from profile data
K_MULTUPLIER = 1e3
M_MULTUPLIER = 1e6
multipliers = {K_MULTUPLIER:    [
                                    'BaseVoltage.nominalVoltage',
                                    'EnergySource.nominalVoltage',
                                    'NoLoadTest.energisedEndVoltage',
                                    'PowerElectronicsConnection.ratedU',
                                    'ShuntCompensator.nomU',
                                    'TapChanger.neutralU',
                                    'TapChangerControl.maxLimitVoltage',
                                    'TapChangerControl.minLimitVoltage',
                                    'TransformerEndInfo.insulationU',
                                    'TransformerEndInfo.ratedU',
                                    'EnergySource.voltageMagnitude'
                                ],
              M_MULTUPLIER:     [
                                    'BatteryUnit.ratedE',
                                    'BatteryUnit.storedE',
                                    'EnergyConsumer.p',
                                    'EnergyConsumer.q',
                                    'EnergyConsumerPhase.p',
                                    'EnergyConsumerPhase.q',
                                    'PowerElectronicsConnection.maxQ',
                                    'PowerElectronicsConnection.minQ',
                                    'PowerElectronicsConnection.p',
                                    'PowerElectronicsConnection.q',
                                    'PowerElectronicsConnection.ratedS',
                                    'PowerElectronicsConnectionPhase.p',
                                    'PowerElectronicsConnectionPhase.q',
                                    'PowerElectronicsUnit.maxP',
                                    'PowerElectronicsUnit.minP',
                                    'TransformerEndInfo.emergencyS',
                                    'TransformerEndInfo.ratedS',
                                    'TransformerEndInfo.shortTermS',
                                    'TransformerTest.basePower'
                                ] 
                }  

class Edge:
    
    def __init__(self, node_qname:QName, element:Element):
        self.node_qname= node_qname
        self.element = element
        self.qname = QName(self.element.tag)
        
    def get_linked_name(self) -> str:
        return self.element.tag.split('.')[-1]

    def set_linked_name(self, name):
        tag = self.element.tag.rsplit(self.get_linked_name(), 1)[:-1][0] + name
        self.element.tag = tag
        self.qname = QName(tag)

    def get_linked_id(self) -> str:
        return self.element.attrib[RDF_RESOURCE]
    
    def is_local(self) -> bool:
        return self.qname.localname.startswith(self.node_qname.localname + '.')
    
    def get_prop_name(self):
        return self.qname.localname
    
    def set_prop_name(self, name):
        new_qname = QName(self.qname.namespace, tag=name)
        self.element.tag = new_qname.text
        self.qname = new_qname
    
    def __eq__(self, other):
        if not isinstance(other, Edge):
            return False
        return str(self.node_qname) == str(other.node_qname) \
               and str(self.qname) == str(other.qname) \
               and self.element.attrib[RDF_RESOURCE] == other.attrib[RDF_RESOURCE]
        
class Literal:
    
    def __init__(self, node_qname, element):
        self.node_qname= node_qname
        self.element = element
        self.qname = QName(self.element.tag)
            
    def is_local(self):
        return self.qname.localname.startswith(self.node_qname.localname + '.')

    def get_prop_name(self):
        return self.qname.localname
    
    def set_prop_name(self, name):
        new_qname = QName(self.qname.namespace, tag=name)
        self.element.tag = new_qname.text
        self.qname = new_qname
        
    def get_val(self):
        return self.element.text
            
    def set_val(self, val:str):
        self.element.text = val
    
    def __eq__(self, other):
        if not isinstance(other, Edge):
            return False
        return str(self.node_qname) == str(other.node_qname) \
               and str(self.qname) == str(other.qname) \
               and self.element.text == other.element.text

class Node:
    
    def __init__(self, element: Element):    
        self.element:Element = element
        self.node_id = self.get_node_id()
        self.qname = QName(self.element.tag)
        self.edges:list[Edge] = []
        self.literals:list[Literal] = []
        self._init_props()
    
    def _init_props(self):
        is_parent = True # Skip first, iterator includes parent
        for prop in self.element.iter():
            if is_parent:
                is_parent = False
                continue
            if self.is_edge_prop(prop):
                self.edges.append(Edge(self.qname, prop))
            else:
                self.literals.append(Literal(self.qname, prop))
    
    def is_edge_prop(self, se):
        return RDF_RESOURCE in se.keys()
                
    def get_node_id(self):
        return self.element.attrib[RDF_ABOUT]
                
    def get_type(self) -> QName :
        return QName(self.element.tag)
    
    def set_type(self, node_type:QName):
        self.element.tag = self.create_tag(node_type.namespace, node_type.localname)
        self.qname = node_type
    
    def change_type(self, node_type:QName, clear=False, include_props=False):
        self.set_type(node_type)
        if clear:
            self.remove_props()
        if include_props:
            pass #TODO
    
    def get_literal_val(self, qname:QName) -> str:
        ret = None
        for literal in self.literals:
            if literal.qname == qname:
                ret = literal.element.text
        return ret

    def has_link(self, node_id):
        ret = False
        for edge in self.edges:
            if edge.get_linked_id() == node_id:
                ret = True
                break
        return ret
        
    def remove_props(self):
        is_parent = True # Skip first, iterator includes parent
        for prop in self.element.iter():
            if is_parent:
                is_parent = False
                continue
            self.element.remove(prop)
        self.edges = []
        self.literals = []
        
    def remove_edge(self, edge, ignore_missing=True):
        try:
            self.element.remove(edge.element)
            self.edges.remove(edge)
        except ValueError:
            if ignore_missing:
                pass
            else:
                raise
            
    def remove_literal(self, literal):
        self.element.remove(literal.element)
        self.literals.remove(literal)
        
    def add_edge(self, element):
        self.add_prop(element.tag, attrib=element.attrib)
        
    def add_prop(self, tag, text=None, attrib=None):
        se = etree.Element(tag, attrib)
        se.tail="\n  "
        if text:
            logging.debug('Add prop text: ' + text)
            se.text = text
        self.element.append(se)
        if self.is_edge_prop(se):
            self.edges.append(Edge(self.qname, se))
        else:
            self.literals.append(Literal(self.qname, se))
        
    def create_tag(self, namespace, localname):
            return f'{{{namespace}}}{localname}'
        
    def get_edges_by_name(self, name):
        edges = []
        for edge in self.edges:
            if edge.get_linked_name() == name:
                edges.append(edge)
        return edges
            
    def move_edges(self, from_node, to_type:QName, keys:list[QName]=[]) -> list[Edge]:        
        to_name = to_type.localname
        edges = self.get_edges_by_name(to_name)
        moved_edges:dict = []
        for edge in edges:
            if edge.get_linked_name() == to_name:
                resource_val = edge.element.attrib[RDF_RESOURCE]
                source_val = self.get_literal_val(keys[0])
                from_val = from_node.get_literal_val(keys[1])
                if source_val and from_val and source_val == from_val:
                    tag:str
                    if edge.is_local():
                        namespace = from_node.qname.namespace
                        localname = '.'.join([from_node.qname.localname, to_name])
                        tag = self.create_tag(namespace, localname)                        
                    else:
                        tag = edge.element.tag                        
                    element = etree.Element(tag, attrib={RDF_RESOURCE:resource_val})
                    from_node.add_edge(element)
                    moved_edges.append(edge)
                    logging.debug('Edge moved:: SOURCE: ' + self.get_node_id() + ' FROM: ' + from_node.get_node_id() + ' TO: ' + resource_val)
        return moved_edges            
        

    def __eq__(self, other):
        if not isinstance(other, Node):
            return False
        return self.get_node_id() == other.get_node_id()
        
class AdapterModel:
        
    def __init__(self, in_filename:str, out_filename:str, subst=[]):        
        self.in_filename = in_filename
        self.out_filename = out_filename
        self.subst = subst
        self.in_tree:ElementTree
        
        # Use a temporary file, do not want to modify input file
        if subst:
            tmp_name:str
            with tempfile.NamedTemporaryFile(mode='w+', delete=False) as tmp:
                tmp_name = tmp.name
                with open(in_filename) as r:
                    text = r.read()
                    for s in subst:
                        text = text.replace(s[0], s[1])    
                    tmp.write(text)
            self.in_tree = etree.parse(tmp_name)
            os.remove(tmp_name)
        else:
            self.in_tree:ElementTree = etree.parse(self.in_filename)
        self.root_node:Element = self.in_tree.getroot()
        self.nodes:list[Node] = self._init_nodes()
        
    def _get_root(self):
        return self.in_tree.getroot()
    
    def get_nsmap(self):
        return self.root_node.nsmap
            
    def _init_nodes(self):
        nodes = []
        element_list = self._get_root().findall('.//*[@' + RDF_ABOUT + ']')
        for e in element_list:
            nodes.append(Node(e))            
        return nodes
            
    def get_nodes_by_type(self, node_type:QName) -> list[Node]:
            return [node for node in self.nodes if node.get_type() == node_type]
        
    def get_node_by_id_type(self, node_id, node_type):
        ret = None
        candidates = self.get_nodes_by_type(node_type)
        for cn in candidates:
            if cn.get_node_id() == node_id:
                ret = cn
                break
        return ret

    def get_out_nodes(self, node, path:list[QName]):
        ret = []        
        if path:
            source_list = [node]
            for p in path:
                path_nodes = []
                for source in source_list:
                    edges = source.get_edges_by_name(p.localname)
                    for edge in edges:
                        linked_node = self.get_node_by_id_type(edge.get_linked_id(), p)
                        if linked_node:
                            path_nodes.append(linked_node)
                source_list = []
                source_list.extend(path_nodes)
            ret = source_list            
        return ret
    
    def get_in_nodes(self, node:Node, node_type:QName):
        ret = []
        node_id = node.node_id
        candidate_nodes = self.get_nodes_by_type(node_type)
        for cn in candidate_nodes:
            if cn.has_link(node_id):
                ret.append(cn)
        return ret
        
    def write_out_file(self):
        self.in_tree.write(self.out_filename, xml_declaration=True, encoding="UTF-8", pretty_print=True)

def in_file_not_exists(filename):
    if not os.path.isfile(filename):
        raise argparse.ArgumentTypeError("{0} does not exist".format(filename))
    return filename

def out_file_exists(filename):
    if os.path.isfile(filename):
        raise argparse.ArgumentTypeError("{0} already exists".format(filename))
    return filename

def setup() -> AdapterModel: 
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', help='filename of the input model', required=True,
                        type=in_file_not_exists, nargs=1)
    parser.add_argument('-o', '--output', help='output filename', required=True,
                        nargs=1)
    args = parser.parse_args()
    return args
    #return AdapterModel(args.input[0], args.output[0])

def epri_to_pnnl(cli_args):
    logging.info('Started epri to pnnl adapter')
    
    ACLSP_NAME = 'ACLineSegmentPhase'
    ACLSP = CIM_NS_LXML + ACLSP_NAME
    ACLS_NAME = 'ACLineSegment'
    ACLS = CIM_NS_LXML + ACLS_NAME
    WSI_NAME = 'WireSpacingInfo'
    WSI = CIM_NS_LXML + WSI_NAME
    WA_NAME = 'WireAssembly'
    WA = CIM_NS_LXML + WA_NAME
    WP_NAME = 'WirePosition'
    WP = CIM_NS_LXML + WP_NAME
    WI_NAME = 'WireInfo'
    WI = CIM_NS_LXML + WI_NAME
    OWI_NAME = 'OverheadWireInfo'
    OWI = CIM_NS_LXML + OWI_NAME
    SN_NAME = 'sequenceNumber'
    WP_SN_LITERAL = CIM_NS_LXML + WP_NAME + '.' + SN_NAME
    ACLSP_SN_LITERAL = CIM_NS_LXML + ACLSP_NAME + '.' + SN_NAME
    IO_NAME = 'IdentifiedObject.name'
    IO_NAME_LITERAL = CIM_NS_LXML + IO_NAME    
    SWITCH_NAME = 'Switch'
    SWITCH = CIM_NS_LXML + SWITCH_NAME
    LBS_NAME = 'LoadBreakSwitch'
    LBS = CIM_NS_LXML + LBS_NAME

    # Get args
    in_file = cli_args.input[0]
    out_file = cli_args.output[0]

    # Create adapter model, with substitutions
    subst = [ ('http://ucaiug.org/61970cim18v02_61968cim14v00#', CIM_NS), 
              ('http://ucaiug.org/GMDM/Exchange#', CIM_NS),
              ('http://ucaiug.org/GMDM#', CIM_NS),
              ('PhotoVoltaicUnit', 'PhotovoltaicUnit')
            ]
    am = AdapterModel(in_file, out_file, subst=subst)

    # Change WireAssembly to WireSpaceingInfo and add default properties
    for wa_node in am.get_nodes_by_type(QName(WA)):
        wa_node_name = wa_node.get_literal_val(QName(IO_NAME_LITERAL))
        wa_node.change_type(QName(WSI), clear=True)
        #wa_node.remove_props()
        wa_node.add_prop(CIM_NS_LXML + IO_NAME, text=wa_node_name)
        wa_node.add_prop(CIM_NS_LXML + 'WireSpacingInfo.usage', 
                      attrib={RDF_RESOURCE:'http://iec.ch/TC57/CIM100#WireUsageKind.distribution'})
        wa_node.add_prop(CIM_NS_LXML + 'WireSpacingInfo.phaseWireCount', text='1')
        wa_node.add_prop(CIM_NS_LXML + 'WireSpacingInfo.phaseWireSpacing', text='0')
        wa_node.add_prop(CIM_NS_LXML + 'WireSpacingInfo.isCable', text='false')

    # Change edges names from WireAssembly to WireSpacingInfo
    for wp_node in am.get_nodes_by_type(QName(WP)):
        for edge in wp_node.edges:
            if edge.get_linked_name() == WA_NAME:
                edge.set_linked_name(WSI_NAME)
    for acls_node in am.get_nodes_by_type(QName(ACLS)):
        for edge in acls_node.edges:
            if edge.get_linked_name() == WA_NAME:
                edge.set_linked_name(WSI_NAME)
                    
    # Move relations WP-R->WI to ACLSP-R->WI
    node_edges_to_remove = []
    aclsp_nodes = am.get_nodes_by_type(QName(ACLSP))
    for aclsp_node in aclsp_nodes:
        logging.debug('aclsp: ' + 'about="' + aclsp_node.get_node_id())
        wsi_nodes = am.get_out_nodes(aclsp_node, [QName(ACLS), QName(WSI)])
        logging.debug('wsi len: ' + str(len(wsi_nodes)))
        for wsi_node in wsi_nodes:
            wp_nodes = am.get_in_nodes(wsi_node, QName(WP))
            logging.debug('wp len: ' + str(len(wp_nodes)))
            for wp_node in wp_nodes:    
                logging.debug('wp: ' + 'about="' + wp_node.get_node_id())
                to_remove = wp_node.move_edges(aclsp_node, QName(WI), (QName(WP_SN_LITERAL), QName(ACLSP_SN_LITERAL)))
                node_edges_to_remove.append((wp_node, to_remove))
        logging.debug('##############')
    for node_edges in node_edges_to_remove:
        node = node_edges[0]
        for edge in node_edges[1]:
            logging.debug("Removed Node: " + node.get_node_id() + ' Linked to: ' + edge.element.attrib[RDF_RESOURCE])
            node.remove_edge(edge, ignore_missing=True)
    
    # Change Class name Switch to LoadBreakSwitch
    for switch_node in am.get_nodes_by_type(QName(SWITCH)):
        switch_node.change_type(QName(LBS))

    # Change Class name WireInfo to OverheadWireInfo
    for wi_node in am.get_nodes_by_type(QName(WI)):
        wi_node.change_type(QName(OWI))

    # Swap edges Equipment.AdditionalEquipmentContainer <-> Equipment.EquipmentContainer
    aec = 'Equipment.AdditionalEquipmentContainer'
    ec = 'Equipment.EquipmentContainer'
    for node in am.nodes:
        for edge in node.edges:
            if edge.get_prop_name() == aec:
                edge.set_prop_name(ec)
            elif edge.get_prop_name() == ec:
                edge.set_prop_name(aec)
            else:
                pass

    # Multipliers
    for node in am.nodes:
        for l in node.literals:
            if l.get_prop_name() in multipliers[K_MULTUPLIER]:
                if l.get_val():
                    l.set_val(str(float(l.get_val()) * K_MULTUPLIER))
            elif l.get_prop_name() in multipliers[M_MULTUPLIER]:
                if l.get_val():
                    l.set_val(str(float(l.get_val()) * M_MULTUPLIER))
            else:
                pass

    # Must be performed after any node creations
    # Add mRID's to all nodes, value is extracted from rdf:about attribute
    for node in am.nodes:
        node_id = node.get_node_id()
        mrid = node_id.rsplit(':', 1)[-1] # Assumes a "urn:uuid:" namespace in rdf:about values
        node.add_prop(CIM_NS_LXML + 'IdentifiedObject.mRID', text=mrid)
        
    # Write output file
    am.write_out_file()
            
    logging.info('Completed epri to pnnl adapter')
                    
                            
if __name__ == '__main__':

    LOG_LEVEL=logging.INFO
    fmt = "%(asctime)s: %(message)s"
    logging.basicConfig(format=fmt, level=LOG_LEVEL, datefmt="%H:%M:%S")    
    
    # Run use-case
    epri_to_pnnl(setup())
    
    