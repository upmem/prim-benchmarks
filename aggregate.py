import os
import json

"""This script aggregates all profiles into one large data set, aggregate.json. Data are presented as : 
"BENCH:TL:BL:DPUS:MEASURE"->[values]

BENCH : name of the bench, example : BFS
TL : number of tasklets
BL : bl parameter of the bench
DPUS : number of dpus
MEASURE : name of the measure, for example "CPU time (ms)"

each value in the list represents one parsing of profile files, in order of aggregate.py invocation.
Note that if there are more than one line in profile files, only the last one is taken in account.
"""

def dict_union(target, source):
    for s in source:
        if not s in target:
            target[s]=source[s]

def parse_benchs(benchs):
    res = dict()
    for d in benchs : 
        print(f"PARSING {d}")
        dict_union(res,parse_profile(os.path.join(d, "profile"), d))
    return res


def parse_profile(profile_dir, bench):
    res = dict()
    if not os.path.isdir(profile_dir) : 
        print(f"{profile_dir} not existing, skipping")
        return res
    for outf in os.scandir(profile_dir):
        print(f"\tparsing {outf}")
        dict_union(res, parse_out(outf, bench))
    return res

def format_identifier(bench, tl, bl, dpus, measure):
    return f"{bench}:{tl}:{bl}:{dpus}:{measure}"

def decode_identifier(identifier):
    s = identifier.split(":")
    return s[0], s[1], s[2], s[3], s[4]

def parse_out(out_file, bench):
    split_file = out_file.name.split("_")
    assert split_file[0] == "out"
    tl = int(split_file[1].replace("tl", ""))
    bl = int(split_file[2].replace("bl", ""))
    dpus = int(split_file[3].replace("dpus",""))
    lines = ""
    with open(out_file, "r") as f :
        lines = f.readlines()
    res = dict()
    for l in lines : 
        if l[0:3] != "CPU": 
            continue
        l_split = l.split("\t")
        for s in l_split :
            ss = s.split(": ") 
            if len(ss) == 2:
                res[format_identifier(bench, tl, bl, dpus, ss[0])] = [float(ss[1])]
    print(res)
    return res

def merge(first, last):    
    fm = 0
    for k in first :
        if len(first[k]) > fm :
            fm = len(first[k])
    lm = 0
    for k in last :
        if len(last[k]) > lm:
            lm = len(last[k])
    res = dict()
    keys = first.keys() | last.keys()
    for k in keys : 
        vf = first.get(k, [])
        if len(vf) != fm : 
            vf = vf + ([float("NaN")] * (fm - len(vf)))
        vl = last.get(k, [])
        if len(vl) != lm : 
            vl = vl + ([float("NaN")] * (lm - len(vl)))
        res[k] = vf + vl
    return res

def from_json(js):
    return json.loads(js)

def to_json(data):
    return json.dumps(data, sort_keys=True, indent=2)


benchs = ["BS", "BFS", "GEMV", "HST-L", "HST-S", "MLP", "NW", "RED", "SCAN-RSS", "SCAN-SSA", "SpMV", "TRNS", "TS", "UNI", "VA"]

data = parse_benchs(benchs)

old = None
if(os.path.isfile("aggregate.json")):
    with open("aggregate.json") as f :
        old = from_json(f.read())

if old != None : 
    data = merge(old, data)

js = to_json(data)

with open("aggregate.json", "w") as f :
    f.write(js)