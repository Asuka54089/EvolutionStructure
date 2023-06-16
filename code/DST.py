import networkx as nx
from tool import load_cost, load_interest
import os


class TccDst:
    def __init__(self, costs):
        self.depth = 2
        self.costs = costs
        self.G = self.full_G()

    def full_G(self):
        G = nx.DiGraph()
        for edge in self.costs:
            G.add_edge(edge[0], edge[1])
        return G

    def subG(self, root):
        # ParentG
        edges = list(nx.bfs_edges(self.G, source=root, depth_limit=self.depth))
        nodes = [root] + [v for u, v in edges]
        subG = self.G.subgraph(nodes)
        return subG

    # init probs
    def init_costs_attrs(self, subG):
        cost_norm_attrs = {}
        for edge in self.costs:
            cost_norm_attrs[edge] = {"cost": self.costs[edge]}

        nx.set_edge_attributes(subG, cost_norm_attrs)
        return subG

    # interest nodes
    def map_interest_nodes(self, subG, root, interests):
        interest_nodes_attrs = {}
        for node in subG.nodes:
            if node in interests:
                interest_nodes_attrs[node] = {"interest_node": True}
            else:
                interest_nodes_attrs[node] = {"interest_node": False}

        interest_nodes_attrs[root] = {"interest_node": True, "root": True}
        nx.set_node_attributes(subG, interest_nodes_attrs)
        return subG

    def directed_steiner_tree(self, subG, root, interest_nodes):
        # Approximation Algorithms for Directed Steiner Problems. SODA 1998: 192-200
        # Moses Charikar, Chandra Chekuri, To-Yat Cheung, Zuo Dai, Ashish Goel, Sudipto Guha, Ming Li
        return resultG

    def remove_cocitaion(self, subG):
        # copy subgraph & direction
        DG = nx.DiGraph(subG)

        norm_prob = {edge: DG.edges[edge]["cost"] for edge in DG.edges}

        topo_order = list(nx.topological_sort(DG))

        # check tri(node0->node2, node0->node1 + node2<-node1)
        remove_edges = []
        recover_edges = []
        update_prob = {edge: norm_prob[edge] for edge in norm_prob}
        for node0 in topo_order:
            node01 = set(DG.successors(node0))
            for node2 in node01:
                node21 = set(DG.predecessors(node2))
                co_citations = node21 & node01
                co_citations = [node for node in co_citations if node in topo_order]
                paths = [(node1, node2) for node1 in co_citations]

                if len(paths) > 0:
                    remove_edges.append((node0, node2))
                for path in paths:
                    if path in recover_edges:
                        update_prob[path] = update_prob[path] + update_prob[(node0, node2)]
                    else:
                        update_prob[path] = update_prob[path] + norm_prob[(node0, node2)]
                    recover_edges.append((node0, path[0], node2))

        # create DG2
        edge_cost_attrs = {}
        for edge in DG.edges:
            edge_cost_attrs[edge] = {"cost": update_prob[edge]}

        edge_cost_attrs = {edge: edge_cost_attrs[edge] for edge in edge_cost_attrs if edge not in remove_edges}

        DG_nococite = nx.DiGraph(DG)
        DG_nococite.remove_edges_from(remove_edges)
        nx.set_edge_attributes(DG_nococite, edge_cost_attrs)

        remove_edges_attr = {(edge[0], edge[1]): {"remove": True} for edge in remove_edges}
        nx.set_edge_attributes(DG, remove_edges_attr)

        recover_edges.reverse()

        return DG, DG_nococite, recover_edges

    def draw_acasteiner(self, subG, Trans_subG, recover_edges, root, interest_nodes):
        resultG = self.directed_steiner_tree(Trans_subG, root, interest_nodes)

        result_nodes_attrs = {}
        result_edges_attrs = {}
        for node in resultG.nodes:
            result_nodes_attrs[node] = {"steiner_node": True}
        for edge in resultG.edges:
            if (edge[0], edge[1]) in Trans_subG.edges:
                result_edges_attrs[(edge[0], edge[1])] = {"steiner_edge": True}
            else:
                result_edges_attrs[edge] = {"steiner_edge": False}

        for edge in recover_edges:
            if (edge[1], edge[2]) in resultG.edges and (edge[0], edge[1]):
                resultG.add_edge(edge[0], edge[2])
                result_edges_attrs[(edge[0], edge[2])] = {"recover": True}

        nx.set_node_attributes(Trans_subG, result_nodes_attrs)
        nx.set_edge_attributes(Trans_subG, result_edges_attrs)
        nx.set_node_attributes(subG, result_nodes_attrs)
        nx.set_edge_attributes(subG, result_edges_attrs)

        return subG, Trans_subG

    def run_acasteiner(self, subG, root, interest_nodes):
        save_path1 = "/" + root + "/tccdst.graphml"
        subG, Trans_subG, recover_edges = self.remove_cocitaion(subG)
        subG, Trans_subG, = self.draw_acasteiner(subG, Trans_subG, recover_edges, root, interest_nodes)
        # save graph
        nx.write_graphml(subG, save_path1)

    def run(self, root, interests):
        path = root + "/"
        if not os.path.exists(path):
            os.makedirs(path)

        subG = self.subG(root)
        subG = self.init_costs_attrs(subG)

        subG_truth = self.map_interest_nodes(subG, root, interests)
        self.run_acasteiner(subG_truth, root, interests)


if __name__ == "__main__":
    cost = load_cost()
    root, interests = load_interest()
    o = TccDst(cost)
    o.run(root, interests)
