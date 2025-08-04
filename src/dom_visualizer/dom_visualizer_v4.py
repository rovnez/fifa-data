import dash
import dash_cytoscape as cyto
from dash import html, dcc, Output, Input, State
from bs4 import BeautifulSoup, Tag
import networkx as nx
import uuid
import copy

# === Load and parse HTML ===
path = "C:\\Users\\bokla\\020_Areas\\data\\fifa-data\\src\\learning\\html_cache\\ruud.html"
with open(path, "r", encoding="utf-8") as f:
    html_f = f.read()
bs = BeautifulSoup(html_f, 'html.parser')

# === Inject persistent data-uid ===
for tag in bs.find_all(True):
    tag['data-uid'] = str(uuid.uuid4())

# === Settings for visibility ===
SHOW_TAGS = {"html", "head", "body", "div"}
HIDE_TAGS = set()  # add any tag names you want to hide entirely

# === Build NetworkX graph from DOM with hidden flag ===
def dom_to_graph(root, graph=None, lookup=None):
    if graph is None:
        graph = nx.DiGraph()
        lookup = {}
    uid = root.attrs['data-uid']
    tag_name = root.name
    # Determine hidden status
    #hidden = tag_name in HIDE_TAGS or tag_name not in SHOW_TAGS
    hidden = False
    label = f"{tag_name}, class={root.get('class')}, id={root.get('id')}, uid={uid}"
    graph.add_node(uid, label=label, hidden=hidden)
    lookup[uid] = root
    for child in root.children:
        if isinstance(child, Tag):
            child_uid = child.attrs['data-uid']
            graph.add_edge(uid, child_uid)
            dom_to_graph(child, graph, lookup)
    return graph, lookup

# Remove nodes flagged hidden, rewiring edges
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

# Build full and visible graphs
graph_full, bs_lookup = dom_to_graph(bs.html or bs)
graph_vis = remove_hidden_nodes(graph_full)

# Determine roots for visual graph
vis_roots = [n for n in graph_vis.nodes if graph_vis.in_degree(n) == 0]
vis_root = vis_roots[0] if vis_roots else None

# Prepare initial Cytoscape elements from visible graph
elements_vis = [
    {'data': {'id': n, 'label': graph_vis.nodes[n]['label']}}
    for n in graph_vis.nodes
] + [
    {'data': {'source': u, 'target': v}}
    for u, v in graph_vis.edges
]

# === Dash App ===
app = dash.Dash(__name__)

app.layout = html.Div(
    style={'display': 'flex', 'flexDirection': 'column', 'height': '100vh'},
    children=[
        html.Div([
            html.H3("DOM Graph Viewer"),
            html.Button("Focus on selected node", id='focus-button', n_clicks=0),
            html.Button("Reset focus", id='reset-button', n_clicks=0, style={'marginLeft': '10px'}),
            cyto.Cytoscape(
                id='dom-graph',
                elements=elements_vis,
                layout={
                    'name': 'breadthfirst',
                    'roots': f'[id = "{vis_root}"]' if vis_root else None,
                    'spacingFactor': 2.5
                },
                style={'width': '100%', 'height': '40vh'}
            )
        ], style={'flex': '0 0 auto', 'padding': '10px'}),

        html.Div(style={'flex': '1', 'display': 'flex', 'padding': '10px', 'gap': '10px'}, children=[
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
                html.Iframe(id='html-subtree-render', style={'width': '100%', 'height': '100%', 'border': '1px solid #ccc'})
            ], style={'flex': '1'}),

            html.Div([
                html.H4("Full Page with Highlight"),
                html.Iframe(id='full-page-preview', style={'width': '100%', 'height': '100%', 'border': '1px solid #ccc'})
            ], style={'flex': '1'})
        ])
    ]
)

# Callback to focus/reset view on the visible graph
@app.callback(
    Output('dom-graph', 'elements'),
    Output('dom-graph', 'layout'),
    Input('focus-button', 'n_clicks'),
    Input('reset-button', 'n_clicks'),
    State('dom-graph', 'tapNodeData')
)
def update_focus(focus_clicks, reset_clicks, tap_data):
    ctx = dash.callback_context
    if not ctx.triggered:
        return elements_vis, {'name': 'breadthfirst', 'roots': f'[id = "{vis_root}"]' if vis_root else None, 'spacingFactor': 2.5}
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if button_id == 'focus-button' and tap_data and 'id' in tap_data:
        sel_uid = tap_data['id']
        descendants = list(nx.descendants(graph_vis, sel_uid)) + [sel_uid]
        elems = [
            {'data': {'id': n, 'label': graph_vis.nodes[n]['label']}} for n in descendants
        ] + [
            {'data': {'source': u, 'target': v}} for u, v in graph_vis.edges if u in descendants and v in descendants
        ]
        return elems, {'name': 'breadthfirst', 'roots': f'[id = "{sel_uid}"]', 'spacingFactor': 2.5}
    # reset
    return elements_vis, {'name': 'breadthfirst', 'roots': f'[id = "{vis_root}"]' if vis_root else None, 'spacingFactor': 2.5}

# Callback for subtree code and previews
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
    cloned = copy.deepcopy(bs)
    sel = cloned.find(attrs={'data-uid': uid})
    if sel:
        sel['id'] = 'selected-subtree'
        style_tag = cloned.new_tag('style')
        style_tag.string = (
            "#selected-subtree { background-color: yellow !important; color: red !important; }"
            "#selected-subtree * { color: red !important; }"
        )
        head = cloned.head or cloned.html
        head.insert(0, style_tag)
    return code, preview, cloned.prettify()

if __name__ == '__main__':
    app.run(debug=True)