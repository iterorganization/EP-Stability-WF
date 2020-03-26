import os, sys
sys.path.append('interface')
sys.path.append('workflow')
sys.path.append('workflow/input')
sys.path.append(os.getcwd())
from lxml import etree



def create_workflow_param_from_file(filepath):
    tree = etree.parse(filepath)
    root = tree.getroot()

    name0 = root[0].attrib['display']
    name1 = root[1].attrib['display']

    workflow_param = {}
    workflow_param = {name0: {}, name1: {}}


    
    for elem in root[0].iter():
        if len(elem) == 0 and elem.tag is not etree.Comment:
            workflow_param[name0][elem.tag] = elem.text

    for elem in root[1].iter():
        if len(elem) == 0 and elem.tag is not etree.Comment:
            workflow_param[name1][elem.tag] = elem.text     


    return(workflow_param)
    
def create_ligka_param_from_file(filepath):
    tree = etree.parse(filepath)
    root = tree.getroot()

    name0 = root.attrib['display']
   

    ligka_param = {}
    ligka_param = {name0: {}}


    
    for elem in root.iter():
        if len(elem) == 0 and elem.tag is not etree.Comment:
            ligka_param[name0][elem.tag] = elem.text


    return(ligka_param)