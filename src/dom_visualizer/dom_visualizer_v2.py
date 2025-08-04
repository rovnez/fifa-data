import dash
import dash_cytoscape as cyto
from dash import html, Output, Input
from bs4 import BeautifulSoup, Tag
import networkx as nx
import uuid
import copy

# === Load and parse HTML ===
path = "/learning/sample_html/nos.html"
#path = "C:\\Users\\bokla\\020_Areas\\data\\fifa-data\\src\\dev_fifa_data\\webscrape\\html_samples\\player_252371-250044.html"

with open(path, "r", encoding="utf-8") as f:
    html_f = f.read()
bs = BeautifulSoup(html_f, 'html.parser')

# === Inject persistent data-uid ===
for tag in bs.find_all(True):
    tag['data-uid'] = str(uuid.uuid4())

# === Settings ===
#SHOW_TAGS = {"html", "head", "body", "div"}
HIDE_TAGS = {}

# === Build NetworkX graph from DOM ===
def dom_to_graph(root, graph=None, lookup=None):
    if graph is None:
        graph = nx.DiGraph()
        lookup = {}

    uid = root.attrs['data-uid']
    label = f"{root.name}, class={root.get('class')}, id={root.get('id')}, uid={uid}"
    #hidden = root.name not in SHOW_TAGS
    # hidden = root.name in HIDE_TAGS
    # if not root.get('class'):
    #     hidden = True
    hidden = False
    graph.add_node(uid, label=label, hidden=hidden)
    lookup[uid] = root

    for child in root.children:
        if isinstance(child, Tag):
            child_uid = child.attrs['data-uid']
            graph.add_edge(uid, child_uid)
            dom_to_graph(child, graph, lookup)
    return graph, lookup


def remove_hidden_nodes(G):
    G2 = G.copy()
    for node in list(G2.nodes):
        if G2.nodes[node].get('hidden'):
            preds = list(G2.predecessors(node))
            succs = list(G2.successors(node))
            for u in preds:
                for v in succs:
                    if u != v:
                        G2.add_edge(u, v)
            G2.remove_node(node)
    return G2

# Build graph
root_tag = bs.html or bs
graph_full, bs_lookup = dom_to_graph(root_tag)
graph_vis = remove_hidden_nodes(graph_full)
root_candidates = [n for n in graph_vis.nodes if graph_vis.in_degree(n) == 0]
root_uid = root_candidates[0] if root_candidates else None

# === Dash App ===
app = dash.Dash(__name__)

# Cytoscape elements
elements = [
    {'data': {'id': n, 'label': graph_vis.nodes[n]['label']}}
    for n in graph_vis.nodes
] + [
    {'data': {'source': u, 'target': v}}
    for u, v in graph_vis.edges
]

# Layout: graph on top, then three side-by-side panels
app.layout = html.Div(style={'display': 'flex', 'flexDirection': 'column', 'height': '100vh'}, children=[
    html.Div([
        html.H3("DOM Graph Viewer"),
        cyto.Cytoscape(
            id='dom-graph',
            elements=elements,
            layout={
                'name': 'breadthfirst',
                'roots': f'[id = "{root_uid}"]' if root_uid else None,
                'spacingFactor': 2.5,
                'directed': True
            },
            style={'width': '100%', 'height': '40vh'}
        )
    ], style={'flex': '0 0 auto'}),

    html.Div(style={'flex': '1', 'display': 'flex', 'padding': '10px', 'gap': '10px', 'overflow': 'hidden'}, children=[
        html.Div([
            html.H4("HTML Subtree (Code)"),
            html.Pre(id='html-subtree-code', style={
                'whiteSpace': 'pre-wrap', 'fontFamily': 'monospace',
                'backgroundColor': '#f9f9f9', 'padding': '10px',
                'border': '1px solid #ccc', 'borderRadius': '5px',
                'height': '100%', 'overflowY': 'auto'
            })
        ], style={'flex': '1'}),

        html.Div([
            html.H4("Rendered HTML Preview"),
            html.Iframe(id='html-subtree-render', style={
                'width': '100%', 'height': '100%', 'border': '1px solid #ccc'
            })
        ], style={'flex': '1'}),

        html.Div([
            html.H4("Full Page with Highlight"),
            html.Iframe(id='full-page-preview', style={
                'width': '100%', 'height': '100%', 'border': '1px solid #ccc'
            })
        ], style={'flex': '1'})
    ])
])

@app.callback(
    Output('html-subtree-code', 'children'),
    Output('html-subtree-render', 'srcDoc'),
    Output('full-page-preview', 'srcDoc'),
    Input('dom-graph', 'tapNodeData')
)
def display_subtree(data):
    default = ("Click a node to view HTML subtree.", "", "")
    if not data or 'id' not in data:
        return default

    uid = data['id']
    tag = bs_lookup.get(uid)
    if not tag:
        return ("Could not resolve HTML for node.", "", "")

    code = tag.prettify()
    preview = str(tag)

    # Clone full DOM and highlight selection
    cloned = copy.deepcopy(bs)
    sel = cloned.find(attrs={'data-uid': uid})
    if sel:
        # Assign ID directly rather than wrap
        sel['id'] = 'selected-subtree'
        style_tag = cloned.new_tag('style')
        style_tag.string = (
            "#selected-subtree { background-color: yellow !important; color: red !important; }"
            "#selected-subtree * { color: red !important; }"
        )
        head = cloned.head or cloned.html
        head.insert(0, style_tag)
    full_page = cloned.prettify()

    return code, preview, full_page

if __name__ == '__main__':
    app.run(debug=True)