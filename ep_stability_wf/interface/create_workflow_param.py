from lxml import etree

def create_workflow_param_from_file(filepath):
    tree = etree.parse(filepath)
    root = tree.getroot()
    workflow_param = {}
    for child in root:
        key = child.attrib.get("display", child.tag)
        workflow_param[key] = element_to_dict(child)
    return workflow_param

def element_to_dict(elem):
    if len(elem) == 0:
        return (elem.text, elem.attrib.get("display"))

    result = {}
    for child in elem:
        if not isinstance(child.tag, str):
            continue
        # For non-leaf children, use the display attribute as the key.
        if len(child) > 0:
            key = child.attrib.get("display", child.tag)
        else:
            key = child.tag
        result[key] = element_to_dict(child)
    return result

def create_xml_from_workflow_param(workflow_param):
    """
    Convert a nested dictionary (as produced by create_workflow_param_from_file)
    back into an XML tree.
    """
    root = etree.Element("root")
    for key, value in workflow_param.items():
        # For non-leaf nodes, key is the display attribute; generate a tag name.
        if isinstance(value, dict):
            tag = normalize_tag(key)
            elem = etree.SubElement(root, tag)
            elem.attrib["display"] = key
            add_children_to_element(elem, value)
        else:
            # For leaf nodes at the top level, key is assumed to be the original tag.
            elem = etree.SubElement(root, key)
            text, display = value
            if display is not None:
                elem.attrib["display"] = display
            elem.text = text
    return root

def add_children_to_element(parent, d):
    """
    Recursively add children to an XML element from the dictionary d.
    For non-leaf items, the key is taken as the display attribute and converted to a tag.
    For leaf items, the key is assumed to be the tag.
    """
    for key, value in d.items():
        if isinstance(value, dict):
            tag = normalize_tag(key)
            child = etree.SubElement(parent, tag)
            child.attrib["display"] = key
            add_children_to_element(child, value)
        else:
            # value is a tuple (text, display) for a leaf node.
            child = etree.SubElement(parent, key)
            text, display = value
            if display is not None:
                child.attrib["display"] = display
            child.text = text

def normalize_tag(name):
    """
    Convert a display name into a plausible XML tag name.
    For example, 'WORKFLOW PARAMETERS' becomes 'workflow_parameters'.
    """
    return name.lower().replace(" ", "_")

def create_xml_param_from_file(filepath):
    tree = etree.parse(filepath)
    root = tree.getroot()

    name0 = root.attrib["display"]

    param = {}
    param = {name0: {}}

    for elem in root.iter():
        if len(elem) == 0 and elem.tag is not etree.Comment:
            if len(elem.text) != "":
                param[name0][elem.tag] = elem.text.strip()
            else:
                param[name0][elem.tag] = elem.text

    return param


def save_xml_param_to_file(ligka_param, filepath):
    tree = etree.parse(filepath)
    root = tree.getroot()

    name0 = root.attrib["display"]
    for elem in root.iter():
        if (elem.tag is not etree.Comment) and (len(elem) == 0):
            elem.text = ligka_param[name0][elem.tag]

    tree.write(filepath)
    file_name = filepath.split("/")[-1]
    print(f"Saved settings to {file_name}!")


def save_xml_param_to_file_multiple(ligka_param, filepath):
    tree = etree.parse(filepath)
    root = tree.getroot()

    for level in root:
        name = level.attrib["display"]
        for elem in level.iter():
            if len(elem) == 0 and elem.tag is not etree.Comment:
                elem.text = ligka_param[name][elem.tag][0]

    tree.write(filepath)
    file_name = filepath.split("/")[-1]
    print(f"Saved settings to {file_name}!")


def save_xml_param_to_file_on_run(filepath, variable, value):
    tree = etree.parse(filepath)
    root = tree.getroot()

    # name0 = root.attrib['display']
    for elem in root.iter():
        if (elem.tag is not etree.Comment) and (len(elem) == 0):
            if elem.tag == variable:
                elem.text = value

    tree.write(filepath)


def save_xml_param_multiple_to_file_on_run(filepath, variable_list, value_list):
    tree = etree.parse(filepath)
    root = tree.getroot()

    # name0 = root.attrib['display']
    for pairs in zip(variable_list, value_list):
        for elem in root.iter():
            if (elem.tag is not etree.Comment) and (len(elem) == 0):
                if elem.tag == pairs[0]:
                    elem.text = pairs[1]

    tree.write(filepath)


def update_xml_param_wf(ligka_param, ref, elem, newvalue, parent = None):
    if parent is None:
        lst = list(ligka_param[ref][elem])
        lst[0] = newvalue
        ligka_param[ref][elem] = tuple(lst)
    else:
        lst = list(ligka_param[parent][ref][elem])
        lst[0] = newvalue
        ligka_param[parent][ref][elem] = tuple(lst)

# Legacy need to check where to use this or not!
def update_xml_param(ligka_param, ref, elem, newvalue):
    ligka_param[ref][elem] = newvalue


def update_xml_param_on_run(ligka_param, elem, newvalue):
    ligka_param["elem"] = newvalue
