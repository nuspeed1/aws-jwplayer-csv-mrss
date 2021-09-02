import enum
import re
from pprint import pprint

def build_path(value, tree={}, vector=[]):
    """
    Given a dict, a vector, and a value, insert the value into the dict
    at the tree leaf specified by the vector.  Recursive!

    Params:
        data (dict): The data structure to insert the vector into.
        vector (list): A list of values representing the path to the leaf node.
        value (object): The object to be inserted at the leaf
    """
    key = vector[0]

    try:
        if len(vector) == 1:
            if isinstance(value, list) and key in tree:
                tree[key] += value
            else:
                tree[key] = value
        else:
            tree[key] = build_path(value, tree[key] if key in tree else {}, vector[1:])
        
        return tree
    except Exception as e:
        print(e)


def get_path(val):
    """
    Finds the path in a string
    Example:
        str = "metadata.tags{guidType\\:$text}"
    Return:
        metadata.tags
    """
    regex = r".+?(?={)|^[\d\w\W]+$"
    match = re.search(regex, val, re.MULTILINE)

    if match:
        return match.group()
    else:
        return None

def get_value_format(exp, val):
    pass


def get_value(exp, val):
    """
    Removes escape character \\
    Replaces $text with val
    Replaces $data with val
    Returns:
        str | list
    """
    # remove escape characters
    tmpl = re.sub(r"\\", "",exp)
    # tmpl = tmpl.replace("$text", val)
    # tmpl = tmpl.replace("$data", val)    
    def replace_vars(v):
        t = tmpl.replace("$text", v)
        t = t.replace("$data", v)
        return t

    if isinstance(val, str):
        tmpl = replace_vars(val)
    elif isinstance(val, list):
        tmpl = [replace_vars(i) for i in val]

    return tmpl

def apply_regex_get_value(exp, val):
    """
    Apply regex found in expression
    Returns value
    """
    
    group = re.split(r"(?<!\\):", exp)

    if len(group) > 1:
        
        exp = group[1].split("regex=")[-1]

        regex = re.compile(exp)

        matches = re.finditer(regex, val)

        res = [str(i.group()).strip() for i in matches]

        return res
    else:
        return False

def get_expression(val):
    """
    Finds the expression in a string
    Example:
        val = "metadata.tags{guidType\\:$text}"
    Return:
        guidType\:$text
    """
    regex = r"(?<={)(.*?)(?=})"
    match = re.search(regex, val, re.MULTILINE)
    if match:
        return match.group()
    else:
        return None

def get_variable_names(strr):
    """
    Find variables formatted with __<VARIABLE>__ and return all results
    Returns:
        list
    """
    regex = r"__([A-Z_]+)__"
    
    matches = re.finditer(regex, strr)
    
    res = []
    res = [m.group() for m in matches]

    return res

def build_load_order(payload):
    """
    This does topological sorting

    Returns:
        list
    """
    p_list = []
    for k in payload:
        p_list.append({k: payload[k]})

    sorted = []
    
    def order(key):
        if "perm" in payload[key]:
            return
        if "temp" in payload[key]:
            pass
        
        payload[key]['temp'] = True
        
        if "dependencies" in payload[key]:
            for d in payload[key]['dependencies']:
                if d in payload:
                    order(d)

        payload[key]['temp'] = False
        payload[key]['perm'] = True

        for i in p_list:
            if key in i:
                sorted.append(i)

    has_more = True
    while has_more:
        for p in payload:
            if "temp" not in p or "perm" not in p:
                order(p)
                
        has_more = False

    return sorted