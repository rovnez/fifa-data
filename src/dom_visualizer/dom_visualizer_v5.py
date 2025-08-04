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

# === Build NetworkX graph from DOM ===
def dom_to_graph(root, graph=None, lookup=None):
    if graph is None:
        graph = nx.DiGraph()
        lookup = {}
    uid = root.attrs['data-uid']
    label = f"{root.name} | class={root.get('class')} | id={root.get('id')}"
    graph.add_node(uid, label=label)
    lookup[uid] = root
    for child in root.children:
        if isinstance(child, Tag):
            child_uid = child.attrs['data-uid']
            graph.add_edge(uid, child_uid)
            dom_to_graph(child, graph, lookup)
    return graph, lookup

graph_full, bs_lookup = dom_to_graph(bs.html or bs)
graph_vis = graph_full  # no hidden‐tag logic here
vis_roots = [n for n in graph_vis if graph_vis.in_degree(n) == 0]
vis_root = vis_roots[0] if vis_roots else None

# Initial full‐graph elements
def make_elements(node_set, folded_set):
    nodes = []
    for n in node_set:
        nodes.append({
            'data': {'id': n, 'label': graph_vis.nodes[n]['label']},
            'classes': 'folded' if n in folded_set else ''
        })
    edges = [
        {'data': {'source': u, 'target': v}}
        for u, v in graph_vis.edges
        if u in node_set and v in node_set
    ]
    return nodes + edges

initial_elements = make_elements(set(graph_vis.nodes), set())

# === Dash App ===
app = dash.Dash(__name__)
app.layout = html.Div(style={'display': 'flex', 'flexDirection': 'column', 'height': '100vh'}, children=[
    html.Div(style={'padding': '10px'}, children=[
        html.H3("DOM Graph Viewer"),
        html.Button("Focus on selected node", id='focus-button', n_clicks=0),
        html.Button("Reset view", id='reset-button', n_clicks=0, style={'marginLeft': '10px'}),
        html.Button("Fold selected node", id='fold-button', n_clicks=0, style={'marginLeft': '10px'}),
        html.Button("Unfold selected node", id='unfold-button', n_clicks=0, style={'marginLeft': '10px'}),
        dcc.Store(id='fold-store', data=[]),
        cyto.Cytoscape(
            id='dom-graph',
            elements=initial_elements,
            layout={
                'name': 'breadthfirst',
                'roots': f'[id = "{vis_root}"]' if vis_root else None,
                'spacingFactor': 2.5
            },
            stylesheet=[
                {'selector': 'node', 'style': {
                    'content': 'data(label)',
                    'font-size': '10px',
                    'background-color': '#BFD7B5'
                }},
                {'selector': '.folded', 'style': {
                    'background-color': 'red'
                }},
                {'selector': 'edge', 'style': {
                    'line-color': '#A3C4BC'
                }}
            ],
            style={'width': '100%', 'height': '40vh'}
        )
    ]),

    html.Div(style={'flex': '1', 'display': 'flex', 'padding': '10px', 'gap': '10px'}, children=[
        html.Div(style={'flex': '1'}, children=[
            html.H4("HTML Subtree (Code)"),
            html.Pre(id='html-subtree-code', style={
                'whiteSpace': 'pre-wrap', 'fontFamily': 'monospace',
                'backgroundColor': '#f9f9f9', 'padding': '10px',
                'border': '1px solid #ccc', 'borderRadius': '5px',
                'height': '100%', 'overflowY': 'auto'
            })
        ]),
        html.Div(style={'flex': '1'}, children=[
            html.H4("Rendered HTML Preview"),
            html.Iframe(id='html-subtree-render', style={'width': '100%', 'height': '100%', 'border': '1px solid #ccc'})
        ]),
        html.Div(style={'flex': '1'}, children=[
            html.H4("Full Page with Highlight"),
            html.Iframe(id='full-page-preview', style={'width': '100%', 'height': '100%', 'border': '1px solid #ccc'})
        ])
    ])
])

# === Callbacks ===

# 1) Maintain folded‐node set
@app.callback(
    Output('fold-store', 'data'),
    Input('fold-button', 'n_clicks'),
    Input('unfold-button', 'n_clicks'),
    State('dom-graph', 'tapNodeData'),
    State('fold-store', 'data'),
    prevent_initial_call=True
)
def update_fold_store(fold_ct, unfold_ct, tap_data, folded):
    if not tap_data or 'id' not in tap_data:
        return folded
    uid = tap_data['id']
    folded_set = set(folded or [])
    trigger = dash.callback_context.triggered[0]['prop_id'].split('.')[0]
    if trigger == 'fold-button':
        folded_set.add(uid)
    elif trigger == 'unfold-button':
        folded_set.discard(uid)
    return list(folded_set)

# 2) Single callback for elements + layout: handles focus, reset, and folds
@app.callback(
    Output('dom-graph', 'elements'),
    Output('dom-graph', 'layout'),
    Input('focus-button', 'n_clicks'),
    Input('reset-button', 'n_clicks'),
    Input('fold-store', 'data'),
    State('dom-graph', 'tapNodeData'),
    prevent_initial_call=True
)
def update_graph(focus_ct, reset_ct, folded, tap_data):
    ctx = dash.callback_context
    trigger = ctx.triggered[0]['prop_id'].split('.')[0]

    # 1) compute which nodes to hide due to folds
    folded_set = set(folded or [])
    to_hide = set()
    for uid in folded_set:
        to_hide |= nx.descendants(graph_vis, uid)
    visible_nodes = set(graph_vis.nodes) - to_hide

    # 2) if focusing
    if trigger == 'focus-button' and tap_data and 'id' in tap_data:
        sel = tap_data['id']
        sub = set(nx.descendants(graph_vis, sel)) | {sel}
        visible_nodes &= sub
        layout = {
            'name': 'breadthfirst',
            'roots': f'[id = "{sel}"]',
            'spacingFactor': 2.5
        }
    else:
        # reset or fold/unfold
        layout = {
            'name': 'breadthfirst',
            'roots': f'[id = "{vis_root}"]' if vis_root else None,
            'spacingFactor': 2.5
        }

    elements = make_elements(visible_nodes, folded_set)
    return elements, layout

# 3) Show HTML subtree & previews
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
    # prettified code
    code = tag.prettify()
    # subtree preview
    preview = str(tag)
    # full page highlight
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
