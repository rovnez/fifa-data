import dash
import dash_cytoscape as cyto
from dash import html, dcc, Output, Input, State
from bs4 import BeautifulSoup, Tag
import networkx as nx
import uuid
import copy

# === Load and parse HTML ===
path = "/learning/sample_html/nos.html"
with open(path, "r", encoding="utf-8") as f:
    html_f = f.read()
bs = BeautifulSoup(html_f, 'html.parser')

# === Inject persistent data-uid ===
for tag in bs.find_all(True):
    tag['data-uid'] = str(uuid.uuid4())

# === Build NetworkX graph from DOM ===
def dom_to_graph(root, graph=None, lookup=None):
    if graph is None:
        graph = nx.DiGraph()
        lookup = {}
    uid = root.attrs['data-uid']
    label = f"{root.name}, class={root.get('class')}, id={root.get('id')}, uid={uid}"
    graph.add_node(uid, label=label)
    lookup[uid] = root
    for child in root.children:
        if isinstance(child, Tag):
            child_uid = child.attrs['data-uid']
            graph.add_edge(uid, child_uid)
            dom_to_graph(child, graph, lookup)
    return graph, lookup

# Build full graph
root_tag = bs.html or bs
graph_full, bs_lookup = dom_to_graph(root_tag)
# No hidden filtering for focus feature

# Prepare initial Cytoscape elements
all_nodes = list(graph_full.nodes)
all_edges = list(graph_full.edges)
initial_elements = [
    {'data': {'id': n, 'label': graph_full.nodes[n]['label']}}
    for n in all_nodes
] + [
    {'data': {'source': u, 'target': v}}
    for u, v in all_edges
]
# Determine original root (in-degree zero)
orig_roots = [n for n in graph_full.nodes if graph_full.in_degree(n) == 0]
orig_root = orig_roots[0] if orig_roots else None

# === Dash App ===
app = dash.Dash(__name__)

app.layout = html.Div(
    style={'display': 'flex', 'flexDirection': 'column', 'height': '100vh'},
    children=[
        html.Div([
            html.H3("DOM Graph Viewer"),
            # Focus button and reset
            html.Button("Focus on selected node", id='focus-button', n_clicks=0),
            html.Button("Reset focus", id='reset-button', n_clicks=0, style={'marginLeft': '10px'}),
            cyto.Cytoscape(
                id='dom-graph',
                elements=initial_elements,
                layout={'name': 'breadthfirst', 'roots': f'[id = "{orig_root}"]' if orig_root else None, 'spacingFactor': 2.5},
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

# Callback to focus or reset graph view
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
        # initial
        return initial_elements, {'name': 'breadthfirst', 'roots': f'[id = "{orig_root}"]' if orig_root else None, 'spacingFactor': 2.5}
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if button_id == 'focus-button' and tap_data and 'id' in tap_data:
        sel_uid = tap_data['id']
        # compute descendants
        descendants = list(nx.descendants(graph_full, sel_uid)) + [sel_uid]
        # filter nodes and edges
        elems = [
            {'data': {'id': n, 'label': graph_full.nodes[n]['label']}} for n in descendants
        ] + [
            {'data': {'source': u, 'target': v}} for u, v in graph_full.edges if u in descendants and v in descendants
        ]
        # new layout roots on selected
        layout = {'name': 'breadthfirst', 'roots': f'[id = "{sel_uid}"]', 'spacingFactor': 2.5}
        return elems, layout
    else:
        # reset
        return initial_elements, {'name': 'breadthfirst', 'roots': f'[id = "{orig_root}"]' if orig_root else None, 'spacingFactor': 2.5}

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
    full_page = cloned.prettify()
    return code, preview, full_page

if __name__ == '__main__':
    app.run(debug=True)
