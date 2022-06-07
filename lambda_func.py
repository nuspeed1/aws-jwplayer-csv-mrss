import json
import csv
import re
from utils import get_expression, get_variable_names, build_load_order
from media import MediaElement
from track import TrackElement
from thumbnail import ThumbnailElement
from poster import PosterElement
from pprint import pprint

def get_jw_mapping(f):
    f = open(f)
    data = json.load(f)
    return data

def load_local_csv_file(f):
    csvfile = open(f, newline="")

    reader = csv.DictReader(csvfile)

    return reader

def get_all_values(nested_dict):
    for key, value in nested_dict.items():
        if type(value) is dict:
            get_all_values(value)
        else:
            print(key, ":", value)

def convert_regex(exp, md):
    """
        Apply regex to metadata value
    Returns:
        A list of formatted values
    """
    try:
        # find sub or split in string
        regex = r"(?<=regex=sub\()(.*?)(?=\)$)|(?<=regex=split\()(.*?)(?=\)$)"
        
        # extract regex expression
        reg_exp = re.search(regex, exp)
        
        # build argument list
        args = reg_exp.group().split("`")

        # remove escape characters
        args = [a.replace("\\\\", "\\") for a in args]
        
        # extract variables__<VARIABLE>__ from expression 
        vars = get_variable_names(reg_exp.group())

        # create keys data lookup
        vars_map = {}
        for v in vars:
            vars_map[v] = md[v]

        response = None
        if "regex=sub" in exp and args[-1] in vars_map:
            #regex find and replace expression found, convert
            value = vars_map[args[-1]]

            response = re.sub(args[0], args[1], value)

            response = [r.strip() for r in response.split(",")]
        elif "regex=split" in exp and args[-1] in vars_map:
            #split expression found, convert
            value = vars_map[args[1]]

            c = re.compile(args[0])

            response = [v.strip() for v in re.split(c, value)]
        else:
            return None

    except Exception as e:
        print(e)
    return response

def call_endpoints(data):
    for d in data:
        t = data[d]['type']
        p = data[d]['payload']
        f = data[d]['file']
        if t == "media":
            media = MediaElement(p,f)
            media.upload()
            data[d]['md'] = media.get_response()
            pass
        elif t == "thumbnail":
            thumbnail = ThumbnailElement(p, f)
            thumbnail.upload()
            data[d]['md'] = thumbnail.get_response()
            pass
        elif t == "track":
            track = TrackElement(p, f)
            track.upload()
            data[d]['md'] = track.get_response()
            pass
        elif t == "poster":
            poster = PosterElement(p, f)
            poster.upload()
            data[d]['md'] = poster.get_response()
            pass

def lambda_function():
    key_file = load_local_csv_file("./key.csv")
    payloads = get_jw_mapping('./payloads.json')

    exp_regex = r"(\${.*?})"

    # loop through each metadata row
    for row in key_file:
        str_payload = json.dumps(payloads)
        
        md_map = {}
        # create metadata map
        for key in row:
            # strip doublequotes
            row[key] = row[key].replace('"',"")
            md_map[f"__{key}__"] = row[key]
        
        # perform data conversion
        matches = re.finditer(exp_regex, str_payload)
        # pprint(md_map)
        exp_map = {}
        for m in matches:
            exp_map[m.group()] = "MAP"

            # extract expression
            exp = get_expression(m.group())
            if exp in md_map:
                #direct mapping, no conversions needed
                exp_map[m.group()] = md_map[exp]
            elif "regex=" in exp:
                exp_map[m.group()] = convert_regex(exp, md_map)
            else:
                # wait for data generation and populate
                pass
            
        # format str payload
        for k in exp_map:
            value = exp_map[k]
            if isinstance(value, list):
                # manually create comma separate list of list items
                value = ", ".join('"' + item + '"' for item in value)
                str_payload = str_payload.replace(f'"{k}"', value)
            else:
                str_payload = str_payload.replace(k, value)

        print(build_load_order(json.loads(str_payload)))

    
lambda_function()


