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
    _,t_s,_,_,_ = decode_identifier(k)
    tl = int(t_s)
    if not tl in d :
        d[tl] = dict()
    insert_measure(d[tl], k, v)

def insert_dpus(d, k, v):
    _,_,_,d_s,_ = decode_identifier(k)
    dpus = int(d_s)
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
        if n_keys  > m :
            m = n_keys
    return m

def plot_measure(ax, times, lbl):
    ax.plot(times, label=lbl)

def plot_group(ax, group):
    ax.set_ylim(0, 1.1)
    for k in group : 
        plot_measure(ax, group[k], k)

def plot_grid(axes, dpus):
    max_j = 0
    i = 0
    for d in sorted(dpus.keys()) : 
        j = 0
        for t in sorted(dpus[d].keys()):
            plot_group(axes[i, j], dpus[d][t])
            axes[i, j].title.set_text(f"{d} dpus {t} tasklets")
            if j == 0 :
                axes[i, j].set_ylabel("performance (normalized)")
            j +=1
        if max_j < j:
            max_j = j
        i+=1
    for j in range(0, max_j): 
        axes[len(dpus.keys()) -1, j].set_xlabel("measure n°")
        

def plot_bench(bench):
    fig = plt.figure(figsize=(count_tasklets(data[bench]) * 5, count_dpus(data[bench])* 4))
    fig.suptitle(f"Benchmark : {bench}", fontsize=20)
    ax = fig.subplots(count_dpus(data[bench]), count_tasklets(data[bench]), sharex=True, sharey=True)
    plot_grid(ax, data[bench])
    #plt.ylim(0, 1.1)
    print(f"setting size to {count_dpus(data[bench])}:{count_tasklets(data[bench])}")
    lines, labels = ax[0, 0].get_legend_handles_labels()
    plt.legend(lines, labels, loc = 'center left', bbox_to_anchor=(1, 0.5))
    plt.gcf().set_dpi(300)
    plt.savefig(f"plot_{bench}.png")

with open("aggregate.json", "r") as f : 
    data = json.loads(f.read())

data = expand_data(data)

with open("expand.json", "w") as f :
    f.write(json.dumps(data, sort_keys=True, indent=2))

for bench in data : 
    print(f"plotting {bench}")
    plot_bench(bench)
