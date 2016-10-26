import networkx as nx

def graph_influence(graph,alpha=0.85, personalization=None, max_iter=100, tol=1e-06, weight='weight', dangling=None):
     """
       Compute the influence of every single node in a graph
       :graph: networkx DiGraph object
       :returns: networkx DiGraph object populated with scores
     """
     pr = nx.pagerank_scipy(graph,alpha,personalization,max_iter,tol,weight,dangling)
     return pr
