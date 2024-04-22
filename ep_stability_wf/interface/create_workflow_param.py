from lxml import etree


def create_workflow_param_from_file(filepath):
    tree = etree.parse(filepath)
    root = tree.getroot()
    workflow_param = {}
    for level in root:
        name = level.attrib["display"]
        if name not in workflow_param:
            temp_dict = {}
        for elem in level.iter():
            if len(elem) == 0 and elem.tag is not etree.Comment:
                temp_dict[elem.tag] = (elem.text, elem.attrib["display"])
        workflow_param[name] = temp_dict

    return workflow_param


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


def update_xml_param_wf(ligka_param, ref, elem, newvalue):
    lst = list(ligka_param[ref][elem])
    lst[0] = newvalue
    ligka_param[ref][elem] = tuple(lst)

# Legacy need to check where to use this or not!
def update_xml_param(ligka_param, ref, elem, newvalue):
    ligka_param[ref][elem] = newvalue


def update_xml_param_on_run(ligka_param, elem, newvalue):
    ligka_param["elem"] = newvalue
