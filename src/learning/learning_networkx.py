import networkx as nx

import matplotlib.pyplot as plt

G = nx.cubical_graph()
subax1 = plt.subplot(121)
nx.draw(G)  # default spring_layout
subax2 = plt.subplot(122)
nx.draw(G, pos=nx.circular_layout(G), node_color='r', edge_color='b')

# %%

G = nx.DiGraph()

# %%

nodes = [1, 2, 3, 4, 5, 6, 7, 8]
# %%
G.add_nodes_from(nodes)

G.add_edges_from([[1, 2], [2, 3], [2, 4], [2, 5], [4, 6], [4, 7], [7, 8]])
# %%

from networkx.drawing.nx_agraph import graphviz_layout

# hierarchical layout
pos = graphviz_layout(G, prog="dot")

# Draw
nx.draw(G, with_labels=True, arrows=True, node_size=1000, node_color='lightblue', font_size=10)
plt.tight_layout()
plt.show()