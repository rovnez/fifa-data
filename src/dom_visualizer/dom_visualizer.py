import dash
import dash_cytoscape as cyto
from dash import html, dcc, Output, Input
from bs4 import BeautifulSoup, Tag
import networkx as nx
from dataclasses import dataclass

# === Load and parse HTML ===
# path = "C:\\Users\\bokla\\020_Areas\\data\\fifa-data\\src\\learning\\sample_html\\gifts.html"
path = "/dev_fifa_data/webscrape/html_samples/player_252371-250044.html"

with open(path, "r", encoding="utf-8") as f:
    html_f = f.read()

bs = BeautifulSoup(html_f, 'html.parser')

# === Settings ===
SHOW_TAGS = {
    "html", "head", "body",

    'div'

}
HIDDEN_TAGS = {'div'}

HIDDEN_TAGS = {
    'tr'

    #   # Root and document structure
    # "html", "head", "body",

    #   # Metadata
    #   "title", "meta", "link", "style", "script", "base",

    #   # Sectioning content
    "header", "footer", "nav", "main", "section", "article", "aside", "address", "h1", "h2", "h3", "h4", "h5", "h6",

    #   # Grouping content
    "div", "p", "hr", "pre", "blockquote", "ol", "ul", "li", "dl", "dt", "dd", "figure", "figcaption", "main",

    #   # Text-level semantics
    "a", "em", "strong", "small", "mark", "abbr", "code", "var", "samp", "kbd", "sub", "sup", "i", "b", "u", "span", "br", "wbr", "time", "data",

    #   # Forms and input
    #   "form", "input", "label", "textarea", "button", "select", "option", "fieldset", "legend", "datalist", "output", "progress", "meter",

    #   # Interactive elements
    #   "details", "summary", "dialog", "menu", "menuitem",

    #   # Embedded content
    "img", "iframe", "embed", "object", "param", "video", "audio", "source", "track", "canvas", "svg", "map", "area", "picture",

    #   # Tables
    "table", "caption", "thead", "tbody", "tfoot", "tr", "td", "th", "col", "colgroup"
}


# === Node definition ===
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
        return f"{self.name}, {self.val_class}, {self.val_id}, {self.id_}"

    def __repr__(self):
        return self.prop_name

    def __str__(self):
        return self.prop_name


def bs_to_tag_node(bs_obj: Tag) -> TagNode:
    return TagNode(
        id_=id(bs_obj),
        name=bs_obj.name,
        show=bs_obj.name in SHOW_TAGS,
        hidden=bs_obj.name not in SHOW_TAGS,
        val_id=bs_obj.attrs.get('id'),
        val_class=next((x for x in bs_obj.attrs.get('class', [])), None)
    )


# === Graph construction ===
def dom_to_graph(node, graph=None, parent_obj=None, bs_lookup=None):
    if graph is None:
        graph = nx.DiGraph()
        bs_lookup = {}

    node_obj = bs_to_tag_node(node)
    graph.add_node(node_obj, label=node_obj.prop_name or None)
    bs_lookup[str(node_obj.id_)] = node  # str ID for Cytoscape

    if parent_obj is not None:
        graph.add_edge(parent_obj, node_obj)

    for child in node.children:
        if isinstance(child, Tag):
            dom_to_graph(child, graph, node_obj, bs_lookup)

    return graph, bs_lookup


def remove_hidden_nodes(G):
    G = G.copy()
    hidden_nodes = [n for n in G.nodes if getattr(n, 'hidden', False)]
    for node in hidden_nodes:
        preds = list(G.predecessors(node))
        succs = list(G.successors(node))
        for u in preds:
            for v in succs:
                if not G.has_edge(u, v):
                    G.add_edge(u, v)
        G.remove_node(node)
    return G


graph_, bs_lookup = dom_to_graph(bs)
graph2_ = remove_hidden_nodes(graph_)

# === Root node for layout ===
root_node_id = next(
    str(n.id_) for n in graph2_.nodes if graph2_.in_degree(n) == 0
)

# === Dash App ===
app = dash.Dash(__name__)

# Prepare Cytoscape elements
elements = [
               {'data': {'id': str(n.id_), 'label': graph2_.nodes[n]['label']}}
               for n in graph2_.nodes
           ] + [
               {'data': {'source': str(u.id_), 'target': str(v.id_)}}
               for u, v in graph2_.edges
           ]

app.layout = html.Div([
    html.H3("DOM Graph Viewer"),
    cyto.Cytoscape(
        id='dom-graph',
        elements=elements,
        layout={
            'name': 'breadthfirst',
            'roots': f'[id = "{root_node_id}"]',
            'spacingFactor': 1.5,
            'directed': True
        },
        style={'width': '100%', 'height': '600px'}
    ),
    html.Hr(),
    html.Div([
        html.Div([
            html.H4("HTML Subtree (Code)"),
            html.Pre(id='html-subtree-code', style={
                'whiteSpace': 'pre-wrap',
                'fontFamily': 'monospace',
                'backgroundColor': '#f9f9f9',
                'padding': '10px',
                'border': '1px solid #ccc',
                'borderRadius': '5px',
                'height': '400px',
                'overflowY': 'auto'
            })
        ], style={'flex': '1', 'marginRight': '10px'}),

        html.Div([
            html.H4("Rendered HTML Preview"),
            html.Iframe(id='html-subtree-render', style={
                'width': '100%',
                'height': '400px',
                'border': '1px solid #ccc'
            })
        ], style={'flex': '1'})
    ], style={'display': 'flex', 'flexDirection': 'row'})
])


@app.callback(
    Output('html-subtree-code', 'children'),
    Output('html-subtree-render', 'srcDoc'),
    Input('dom-graph', 'tapNodeData')
)
def display_subtree(data):
    if data is None:
        return "Click a node to view HTML subtree.", ""

    tag_id_str = data['id']
    tag_obj = bs_lookup.get(tag_id_str)
    if tag_obj:
        html_code = tag_obj.prettify()
        return html_code, str(tag_obj)
    return f"Could not resolve HTML for node ID: {tag_id_str}", ""


if __name__ == '__main__':
    app.run(debug=True)
