import argparse
import os
import xml.etree.ElementTree as ET
from lxml import etree, objectify
from xml.dom import minidom

#echo=True
echo=False

class Node(object):
    def __init__(self, tag=None, attrib=None, text=None, children=None, uuid=None):
        self.tag = tag
        self.attrib = attrib
        self.text = text            # if has text, then no children
        self.children = children    # list of Node, if has children, then no text
        self.uuid = uuid

    def __eq__(self, other):
        if not isinstance(other, Node):
            return False
        if self.children:
            return NotImplemented
        if other.children:
            return NotImplemented
        return self.tag == other.tag \
               and self.attrib == other.attrib \
               and self.text == other.text \
               and self.uuid == other.uuid


class XMLFile(object):
    def __init__(self, tag=None, attrib=None, namespaces=None, namespacedict=None, children=None):
        self.tag = tag
        self.attrib = attrib
        self.namespaces = namespaces    # dictionary
        self.namespacedict = namespacedict    # dictionary
        self.children = children        # list of Node


class ModelCombiner(object):
    def __init__(self):
        self.base_file_list = []
        self.supp_file_list = []
        self.completeFile = XMLFile()
        self.base_node_id_dict = {}
        self.rdf_namespace = ""
        self.supplement_nodes = []
        self.supplement_node_id_dict = {}
        self.output_filename = ""

    def _check_has_identifiedobject_name(self, node):
        for chld in node.children:
            t = str(chld.tag).split('}')
            if len(t) == 2 and t[1] == "IdentifiedObject.name":
                return True
        return False

    def _add_supp_to_base(self):
        for id, nlist in self.base_node_id_dict.items():
            if echo:
                print(id)
            if len(nlist) > 1:
                gnodes = nlist[0]
                if echo:
                    print('gnodes:')
                    print(gnodes.tag)
                    print(gnodes.attrib)
                hasName = self._check_has_identifiedobject_name(gnodes)
                for node in nlist[1:]:
                    for chld in node.children:
                        if echo:
                            print(chld.tag)
                            print(chld.attrib)
                        if chld not in gnodes.children:
                            t = str(chld.tag).split('}')
                            if len(t) == 2 and t[1] == "IdentifiedObject.name":
                                if not hasName:
                                    gnodes.children.append(chld)
                                    hasName = True
                            else:
                                gnodes.children.append(chld)

    def combine_files(self):
        self.parse_base_files(self.base_file_list)
        if self.supp_file_list:
            self.parse_supp_files(self.supp_file_list)
        self._add_supp_to_base()
        self._write_xml_file()

    def parse_base_files(self, files):
        for b in files:
            self.parse_base_file(b)

    def _get_namespace(self, namespace, nsmap):
        for k, v in nsmap.items():
            if v not in namespace:
                namespace[v] = k
            if k.lower() == "rdf" and not self.rdf_namespace:
                self.rdf_namespace = v

    def _get_id(self, attrib):
        for k, v in attrib.items():
            if self.rdf_namespace in k:
                frags = str(v).split("_")
                return frags[-1]
        return None

    def _read_node(self, child, alist, adict=None):
        if child.tag != 'comment':
            new_child = Node(tag=child.tag)
            new_child.attrib = self._xml_attrib_to_dict(child.attrib)
            thisid = self._get_id(child.attrib)
            existing_node = False
            if thisid:
                new_child.uuid = thisid
                if adict is not None:
                    if thisid not in adict:
                        adict[thisid] = []
                    else:
                        existing_node = True
                    adict[thisid].append(new_child)
            if echo:
                print(child.tag)
                print(child.attrib)
            if child.text:
                new_child.text = child.text.strip()
                if echo:
                    print(new_child.text)
            child_nodes = child.getchildren()
            if child_nodes:
                new_child.children = []
                for gchild in child_nodes:
                    self._read_node(gchild, new_child.children)
            if not existing_node:
                alist.append(new_child)

    def parse_base_file(self, filename):
        with open(filename, encoding='utf8') as fobj:
            xml = fobj.read()
            root = etree.fromstring(xml.encode('utf-8'), parser=objectify.makeparser(remove_blank_text=True))
            if not self.completeFile.namespacedict:
                self.completeFile.namespacedict = {}
                self.completeFile.tag = root.tag
                self.completeFile.attrib = self._xml_attrib_to_dict(root.attrib)
            self._get_namespace(self.completeFile.namespacedict, root.nsmap)
            child_nodes = root.getchildren()
            if child_nodes:
                if not self.completeFile.children:
                    self.completeFile.children = []
                for child in child_nodes:
                    self._read_node(child, self.completeFile.children, adict=self.base_node_id_dict)

    def parse_supp_files(self, files):
        for s in files:
            self.parse_supp_file(s)

    def parse_supp_file(self, filename):
        with open(filename) as fobj:
            xml = fobj.read()
            root = etree.fromstring(xml.encode('utf-8'), parser=objectify.makeparser(remove_blank_text=True))
            if not self.completeFile.namespacedict:
                self.completeFile.namespacedict = {}
            self._get_namespace(self.completeFile.namespacedict, root.nsmap)
            # self.completeFile.tag = root.tag
            # self.completeFile.attrib = root.attrib
            child_nodes = root.getchildren()
            if child_nodes:
                if not self.supplement_nodes:
                    self.supplement_nodes = []
                for child in child_nodes:
                    self._read_node(child, self.completeFile.children, adict=self.base_node_id_dict)

    def input_file_exists(self, filename):
        if not os.path.isfile(filename):
            raise argparse.ArgumentTypeError("{0} does not exist".format(filename))
        return filename

    def setup(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('-b', '--base', help='base file(s) of the model', required=True,
                            type=self.input_file_exists, nargs='+')
        parser.add_argument('-s', '--supplement', help='supplemental file(s) of the model', type=self.input_file_exists,
                            nargs='+')
        parser.add_argument('-o', '--output', help='output file name', required=True, type=str)
        args = parser.parse_args()
        for b in args.base:
            self.base_file_list.append(b)
        if args.supplement:
            for s in args.supplement:
                self.supp_file_list.append(s)
        self.output_filename = args.output

    def _write_xml_file(self):
        for k, v in self.completeFile.namespacedict.items():
            ET.register_namespace(v, k)
        root = ET.Element(self.completeFile.tag)
        for chld in self.completeFile.children:
            if chld.children is not None:
                child = ET.SubElement(root, chld.tag, attrib=chld.attrib)
                for gchld in chld.children:
                    gchild = ET.SubElement(child, gchld.tag, attrib=gchld.attrib)
                    gchild.text = gchld.text
        rough_string = ET.tostring(root, 'utf-8')
        reparsed = minidom.parseString(rough_string)
        with open(self.output_filename, "w") as f:
            f.write(reparsed.toprettyxml(indent="  "))

    def _xml_attrib_to_dict(self, attrib):
        adict = {}
        for k, v in attrib.items():
            adict[k] = v
        return adict

def combine_xml_files (input_root_name, output_filename, extensions=None):
    md = ModelCombiner()
    if extensions:
      for ext in extensions:
        filename = '{:s}{:s}'.format (input_root_name, ext)
        print('adding', filename)
        md.base_file_list.append(filename)
    else:
      for ext in ['CAT', 'EP', 'FUN', 'GEO', 'SSH', 'TOPO']:
        filename = '{:s}_{:s}.XML'.format (input_root_name, ext)
        md.base_file_list.append(filename)
    md.output_filename = output_filename
    md.combine_files()

if __name__ == '__main__':
    md = ModelCombiner()
    md.setup()
    md.combine_files()
