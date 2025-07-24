path = "C:\\Users\\bokla\\020_Areas\\data\\fifa-data\\src\\dev_fifa_data\\webscrape\\html_samples\\player_252371-250044.html"

with open(path, "r", encoding="utf-8") as f:
    html_f = f.read()

from bs4 import BeautifulSoup

bs = BeautifulSoup(html_f, 'html.parser')

# %%

import networkx as nx


def dom_to_graph(node, graph=None, parent_id=None):
    if graph is None:
        graph = nx.DiGraph()
        parent_id = None
    node_id = id(node)
    graph.add_node(node_id, label=node.name or '[text]')
    if parent_id is not None:
        graph.add_edge(parent_id, node_id)
    for child in node.children:
        if getattr(child, 'name', None):
            dom_to_graph(child, graph, node_id)
    return graph


# %%

graph = dom_to_graph(bs)

# %%

import dash
import dash_cytoscape as cyto
from dash import html


def create_dash_app(graph):
    app = dash.Dash(__name__)
    elements = [
                   {'data': {'id': str(n), 'label': graph.nodes[n]['label']}}
                   for n in graph.nodes
               ] + [
                   {'data': {'source': str(u), 'target': str(v)}}
                   for u, v in graph.edges
               ]
    app.layout = html.Div([
        cyto.Cytoscape(
            id='dom-graph',
            elements=elements,
            layout={
                'name': 'breadthfirst',
            },
            style={'width': '100%', 'height': '800px'}
        )

    ])
    return app


app = create_dash_app(graph)

app.run()
