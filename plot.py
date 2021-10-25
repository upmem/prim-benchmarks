import json
import matplotlib.pyplot as plt

def format_identifier(bench, tl, bl, dpus, measure):
    return f"{bench}:{tl}:{bl}:{dpus}:{measure}"

def decode_identifier(identifier):
    s = identifier.split(":")
    return s[0], s[1], s[2], s[3], s[4]

def invert(times):
    n = list()
    for t in times :
        n.append(1/t)
    return n

def normalize(times):
    m = max(times)
    n = list()
    for t in times : 
        n.append(t/m)
    return n

def time_to_speed_factor(times):
    factors = list()
    factors.append(0)
    i = 1
    while(i < len(times)):
        speed_old = 1/times[i-1]
        speed_new = 1/times[i]
        factor = speed_new / speed_old
    #    if factor < 1 : 
    #        factor = - 1 / factor
        factors.append(factor)
        i+=1
    return factors

def insert_measure(d, k, v):
    _,_,_,_,m = decode_identifier(k)
    d[m.replace("Time (ms)","")] = normalize(invert(v))

def insert_tl(d, k, v):
    _,tl,_,_,_ = decode_identifier(k)
    if not tl in d :
        d[tl] = dict()
    insert_measure(d[tl], k, v)

def insert_dpus(d, k, v):
    _,_,_,dpus,_ = decode_identifier(k)
    if not dpus in d :
        d[dpus] = dict()
    insert_tl(d[dpus], k ,v)

def insert_bench(d, k, v): 
    bench,_,_,_,_ = decode_identifier(k)
    if not bench in d : 
        d[bench] = dict()
    insert_dpus(d[bench], k, v)

def expand_data(data):
    res = dict()
    for k in data :
        insert_bench(res, k, data[k])
    return res

def count_dpus(dpus):
    return len(dpus.keys())

def count_tasklets(dpus):
    m = 0
    for d in dpus : 
        n_keys = len(dpus[d].keys())
        if(n_keys) > m :
            m = n_keys
    return m

def plot_measure(ax, times, lbl):
    ax.plot(times, label=lbl)

def plot_group(ax, group):
    ax.set_ylim(0, 1.1)
    for k in group : 
        plot_measure(ax, group[k], k)

def plot_grid(axes, dpus):
    i = 0
    for d in dpus : 
        j = 0
        for t in dpus[d]:
            plot_group(axes[i, j], dpus[d][t])
            j +=1
        i+=1

with open("aggregate.json", "r") as f : 
    data = json.loads(f.read())

data = expand_data(data)

with open("expand.json", "w") as f :
    f.write(json.dumps(data, sort_keys=True, indent=2))

bench = "bench"
tl = 1
dpus = 64

fg, ax = plt.subplots(count_dpus(data["BS"]), count_tasklets(data["BS"]))

plot_grid(ax, data["BS"])

plt.ylim(0, 1.1)

print(f"setting size to {count_dpus(data['BS'])}:{count_tasklets(data['BS'])}")

lines, labels = ax[0, 0].get_legend_handles_labels()
plt.legend(lines, labels, loc = 'lower center')
plt.gcf().set_size_inches(count_dpus(data["BS"]) * 10, count_tasklets(data["BS"]) * 2)
plt.gcf().set_dpi(300)

plt.savefig("plot.png")

