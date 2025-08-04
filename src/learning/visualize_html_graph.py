# path = "C:\\Users\\bokla\\020_Areas\\data\\fifa-data\\src\\dev_fifa_data\\webscrape\\html_samples\\player_252371-250044.html"

path = "C:\\Users\\bokla\\020_Areas\\data\\\\fifa-data\\src\\learning\\sample_html\\gifts.html"

with open(path, "r", encoding="utf-8") as f:
    html_f = f.read()

from bs4 import BeautifulSoup, Tag

bs = BeautifulSoup(html_f, 'html.parser')

# %%


# %%
import networkx as nx

from dataclasses import dataclass

SHOW_TAGS = {
    'tr'

    #   # Root and document structure
    # "html", "head", "body",

    #   # Metadata
    #   "title", "meta", "link", "style", "script", "base",

    #   # Sectioning content
    # "header", "footer", "nav", "main", "section", "article", "aside", "address", "h1", "h2", "h3", "h4", "h5", "h6",

    #   # Grouping content
    # "div", "p", "hr", "pre", "blockquote", "ol", "ul", "li", "dl", "dt", "dd", "figure", "figcaption", "main",

    #   # Text-level semantics
    #   "a", "em", "strong", "small", "mark", "abbr", "code", "var", "samp", "kbd", "sub", "sup", "i", "b", "u", "span", "br", "wbr", "time", "data",

    #   # Forms and input
    #   "form", "input", "label", "textarea", "button", "select", "option", "fieldset", "legend", "datalist", "output", "progress", "meter",

    #   # Interactive elements
    #   "details", "summary", "dialog", "menu", "menuitem",

    #   # Embedded content
    #   "img", "iframe", "embed", "object", "param", "video", "audio", "source", "track", "canvas", "svg", "map", "area", "picture",

    #   # Tables
    #   "table", "caption", "thead", "tbody", "tfoot", "tr", "td", "th", "col", "colgroup"
}

HIDDEN_TAGS = {'div'}


@dataclass(frozen=True)
class TagNode:
    id_: int
    name: str
    show: bool
    hidden: bool
    val_id: str
    val_class: str

    @property
    def prop_name(self) -> str:
        return f"{self.name}, {self.val_class}, {self.val_id}, {self.id_})"

    def __repr__(self):
        return f"{self.name}, {self.val_class}, {self.val_id}, {self.id_})"

    def __str__(self):
        return f"{self.name}, {self.val_class}, {self.val_id}, {self.id_})"


def bs_to_tag_node(bs_obj: BeautifulSoup) -> TagNode:
    return TagNode(id_=id(bs_obj), name=bs_obj.name, show=bs_obj.name in SHOW_TAGS, hidden=bs_obj.name in HIDDEN_TAGS, val_id=bs_obj.attrs.get('id'), val_class=next((x for x in bs_obj.attrs.get('class', [])), None))


def dom_to_graph(node, graph=None, parent_obj=None):
    if graph is None:
        graph = nx.DiGraph()
        parent_obj = None
    if node.name in SHOW_TAGS:
        pass
    node_obj = bs_to_tag_node(node)
    graph.add_node(node_obj, label=node_obj.prop_name or None)
    if parent_obj is not None:
        graph.add_edge(parent_obj, node_obj)
    for child in node.children:
        if getattr(child, 'name', None):
            dom_to_graph(child, graph, node_obj)
    return graph


def remove_hidden_nodes(G):
    G = G.copy()  # Work on a copy to avoid modifying during iteration

    hidden_nodes = [n for n in G.nodes if getattr(n, 'hidden', False)]
    for node in hidden_nodes:
        preds = list(G.predecessors(node))
        succs = list(G.successors(node))

        # Rewire edges: connect each predecessor to each successor
        for u in preds:
            for v in succs:
                if not G.has_edge(u, v):
                    G.add_edge(u, v)

        G.remove_node(node)

    return G


# %%


graph_ = dom_to_graph(bs)
graph2_ = remove_hidden_nodes(graph_)

#graph2_ = graph_.copy()


def get_root(graph: nx.DiGraph):
    return next((n for n in graph.nodes if graph.in_degree(n) == 0), None)


# %%

# %%

import dash
import dash_cytoscape as cyto
from dash import html

root_node_id = [str(n) for n in graph2_.nodes if graph2_.in_degree(n) == 0][0]


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
                'roots': '[id = "{}"]'.format(root_node_id)
            },
            style={'width': '100%', 'height': '800px'}
        )

    ])
    return app


app = create_dash_app(graph2_)

app.run()
