def load():
    feature = load_feature()
    weight = load_weight()
    return weight, feature


def load_weight():
    weight = {}
    file = open("data/" + "feature.txt", 'r')
    for line in file:
        line = line.split(" ")
        u = line[0]
        v = line[1]
        p = float(line[2].strip())
        weight[(u, v)] = p
    return weight


def load_feature():
    set_file = open("data/" + "feature.txt", 'r')
    feature_set = {}
    for line in set_file:
        line = line.split("\t")
        v = line[0]
        f_set = line[1].strip() if len(line[1].strip()) > 0 else []
        f_set = set(f_set.split(","))
        feature_set[v] = f_set
    return feature_set

def load_cost():
    cost = {}
    file = open("data/" + "cost.txt", 'r')
    for line in file:
        line = line.split(" ")
        u = line[0]
        v = line[1]
        p = float(line[2].strip())
        cost[(u, v)] = p
    return cost

def load_interest():
    f_nodes = open("/data/interest.txt", 'r')
    nodes = []
    for line in f_nodes:
        line = line[:-1].split(" ")
        root = line[0]
        nodes = line[1:]
    return root,nodes
