from networkx.classes import Graph

def empty_graph(n=0, create_using=None, default=Graph):
    if create_using is None:
        G = default()
    elif hasattr(create_using, "__call__"):
        G = create_using()
    else:
        G = create_using
        if hasattr(G, 'clear'):
            G.clear()
    if isinstance(n, (list, tuple, set)):
        G.add_nodes_from(n)
    else:
        G.add_nodes_from(range(n))
    return G
