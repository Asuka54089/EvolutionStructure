import networkx as nx
from tool import load

class CCFG(object):
    def __init__(self, weight, feature):
        self.weight = weight
        self.node_set = feature
        self.G = self.initG(self.weight)

        self.Sent = self.init_sent(self.weight, self.G)
        self.Recv = {}
        self.Result = {}
        self.Part1_kxid = {}
        self.Part2_kxid = {}

    def initG(self, weights):
        G = nx.DiGraph()
        for edge in weights:
            G.add_edge(edge[0], edge[1])
        return G

    def init_sent(self, edge_weights, G):
        Sent = {}
        for e in G.edges():
            if e in edge_weights:
                Sent[e] = edge_weights[e]
            else:
                Sent[e] = 0
        return Sent

    def jaccard_sim(self, v0, v2):
        intersection_set = self.node_set[v0] & self.node_set[v2]
        union_set = self.node_set[v0] | self.node_set[v2]
        return len(intersection_set) / len(union_set)

    def Compare(self, v0, v2):
        if v0 in self.node_set and v2 in self.node_set:
            intersection_set = self.node_set[v0] & self.node_set[v2]
            if len(intersection_set) > 0:
                return True

        return False

    def prepare_part1(self, i):
        part1 = {}
        for k in self.G.predecessors(i):
            candiate_prob = {x: self.Sent[(k, x)] for x in self.G.successors(k)}
            if len(candiate_prob) >= 2:
                key1 = max(candiate_prob, key=candiate_prob.get)
                max_value1 = candiate_prob[key1]
                del candiate_prob[key1]
                key2 = max(candiate_prob, key=candiate_prob.get)
                max_value2 = candiate_prob[key2]
            else:
                key1 = max(candiate_prob, key=candiate_prob.get)
                max_value1 = candiate_prob[key1]
                key2 = {"-"}
                max_value2 = 0
            part1[k] = [(key1, max_value1), (key2, max_value2)]
        return part1

    def update_sent(self, i, j, part1):
        print("update_sent", i, j)
        sum_k_list = []
        sum_kxid = []
        for k in self.G.predecessors(i):
            if self.Compare(k, j) == 0 and part1[k][0] == i:
                sum_k_list.append(part1[k][1][1])
                sum_kxid.append((k, part1[k][1][0]))
            else:
                sum_k_list.append(part1[k][0][1])
                sum_kxid.append((k, part1[k][0][0]))

        sum_k = sum(sum_k_list)
        return self.weight[(i, j)] + sum_k, sum_kxid

    def update_recv(self, i, j, part2):
        print("update_recv", i, j)
        recv_temp = 0
        jjkx = ("-", "-")
        for jp in self.G.successors(j):
            if self.Compare(jp, i) == 0:
                sum_k_list = []
                sum_kxid = []
                for k in self.G.predecessors(j):
                    if k != i:
                        if self.Compare(k, jp) == 0 and part2[k][0] == j:
                            sum_k_list.append(part2[k][1][1])
                            sum_kxid.append((k, part2[k][1][0]))
                        else:
                            sum_k_list.append(part2[k][0][1])
                            sum_kxid.append((k, part2[k][0][0]))
                if self.Sent[j, jp] + self.weight[(j, jp)] + sum(sum_k_list) > recv_temp:
                    recv_temp = self.Sent[j, jp] + self.weight[(j, jp)] + sum(sum_k_list)
                    jjkx = (jp, sum_kxid)
        return recv_temp, jjkx

    def fg(self):
        Counter = {}
        for v in self.G:
            Counter[v] = len(list(self.G.predecessors(v)))
        Q = [v for v in Counter if Counter[v] == 0]

        pointer = 0
        L = len(Q)
        while pointer < L:
            i = Q[pointer]
            pointer = pointer + 1
            part1 = self.prepare_part1(i)
            for j in self.G.successors(i):
                sentij, ijkx_id = self.update_sent(i, j, part1)
                self.Sent[(i, j)] = sentij
                self.Part1_kxid[(i, j)] = ijkx_id
                Counter[j] = Counter[j] - 1
                if Counter[j] == 0:
                    Q.append(j)
            L = len(Q)

        pointer = pointer - 1
        while pointer >= 0:
            j = Q[pointer]
            part2 = self.prepare_part1(j)
            if list(self.G.successors(j)) != []:
                for jp in self.G.successors(j):
                    self.Result[(j, jp)] = self.Recv[(j, jp)] + self.Sent[(j, jp)]

            x = list(self.G.predecessors(j))
            for id, i in enumerate(x):
                recvij, jjkx_id = self.update_recv(i, j, part2)
                self.Recv[(i, j)] = recvij
                self.Part2_kxid[(i, j)] = jjkx_id

            pointer = pointer - 1

    def save_fg(self):
        f_fg = open("ccfg.txt", 'w')
        for edge in self.Result:
            f_fg.write(" ".join(map(str, edge)) + " " + str(self.Result[edge]) + "\n")


if __name__ == "__main__":
    method,feature = load()
    o = CCFG(method, feature)
    o.fg()
    o.save_fg()