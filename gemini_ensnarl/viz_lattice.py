"""Plotly/matplotlib visualization helpers for the synthetic-lattice notebook."""

import numpy as np
import networkx as nx
import plotly.graph_objects as go
import plotly.io as pio
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib import colormaps


def matplotlib_to_plotly_colorscale(cmap_name='seismic', n_levels=256):
    cmap = plt.colormaps.get_cmap(cmap_name)
    return [
        [i / (n_levels - 1), mcolors.to_hex(cmap(i / (n_levels - 1)))]
        for i in range(n_levels)
    ]


def node_trace(G, pos, color='#3f3f40', size=8, nstart=0, label=True):
    x, y, z = zip(*[pos[n] for n in G.nodes()])
    if label:
        return go.Scatter3d(
            x=x, y=y, z=z,
            mode='markers+text',
            marker=dict(size=size, color=color),
            text=[str(n+nstart) for n in G.nodes()],
            textposition='top center',
            hoverinfo='text'
        )
    else:
        return go.Scatter3d(
            x=x, y=y, z=z,
            mode='markers',
            marker=dict(size=size, color=color),
            text=[str(n) for n in G.nodes()],
            textposition='top center',
            hoverinfo='text'
        )


def edge_trace(G, pos, color, width=8):
        edge_x, edge_y, edge_z = [], [], []
        for u, v in G.edges():
            x0, y0, z0 = pos[u]
            x1, y1, z1 = pos[v]
            edge_x += [x0, x1, None]
            edge_y += [y0, y1, None]
            edge_z += [z0, z1, None]
        return go.Scatter3d(
            x=edge_x, y=edge_y, z=edge_z,
            mode='lines',
            line=dict(color=color, width=width),
            hoverinfo='none',
            showlegend=False
        )


def edge_trace_constant(G, pos, values, color_scale, width=8, vmin=None, vmax=None):
    """Edge trace with a constant color per edge (from values)."""
    edge_list = list(G.edges())

    if vmin is None:
        vmin = np.min(values)
    if vmax is None:
        vmax = np.max(values)
    norm = mcolors.Normalize(vmin=vmin, vmax=vmax)
    cmap = plt.colormaps.get_cmap(color_scale)

    traces = []
    for i, (u, v) in enumerate(edge_list):
        val = values[i]
        color = mcolors.to_hex(cmap(norm(val)))
        x, y, z = zip(pos[u], pos[v])
        traces.append(go.Scatter3d(
            x=[x[0], x[1], None],
            y=[y[0], y[1], None],
            z=[z[0], z[1], None],
            mode='lines',
            line=dict(color=color, width=width),
            hoverinfo='none'
        ))
    return traces


def dummy_colorbar_trace(vmin, vmax, colorscale, xval=0.8, thickness=20, len=0.4):
    return go.Scatter3d(
        x=[None], y=[None], z=[None],
        mode='markers',
        marker=dict(
            size=0.1,
            color=[vmin, vmax],
            colorscale=colorscale,
            cmin=vmin,
            cmax=vmax,
            colorbar=dict(
                # title='|Column Sum|',
                # titleside='right',
                thickness=thickness,
                len=len,
                x=xval
            )
        ),
        showlegend=False,
        hoverinfo='none'
    )


def plot_networkx_12label(G1, G2, pos1, pos2, camera, lab_name='graph',
                          figsize=(700, 600), row_c='#8a8a8a', col_c='#2159d1',
                          width=10, nlabel=True):
    """Plot the two networks with edge color specified
    Params:
    ------
    """

    # ----------------------------
    # Build plot traces

    # Nodes (same for both graphs)
    trace_nodes_G1 = node_trace(G1, pos1, label=nlabel)
    trace_nodes_G2 = node_trace(G2, pos2, nstart=len(G1.nodes()), label=nlabel)

    # Edges
    trace_edges_G1 = edge_trace(G1, pos1, row_c, width=width)
    trace_edges_G2 = edge_trace(G2, pos2, col_c, width=width)

    # ----------------------------
    # Assemble figure

    fig = go.Figure(data=[
        trace_nodes_G1,
        trace_edges_G1,
        trace_nodes_G2,
        trace_edges_G2
    ])

    axisFormat = dict(
                showbackground=False,
                showticklabels=False,
                autorange=True,
                showgrid=False,
        )


    fig.update_layout(
        # title="Graph Edge Visualization with Lam_gli Row/Column Sums",
        scene=dict(
            xaxis=dict(title='x'),
            yaxis=dict(title='y'),
            zaxis=dict(title='z'),
            aspectmode="data",
        ),
        showlegend=False,
        margin=dict(l=0, r=0, b=0, t=0),
        height=700
    )

    #set an appropriate camera
    camera = camera
    fig.update_layout(scene_camera=camera)

    pio.write_image(fig, lab_name+'.png', width=figsize[0], height=figsize[1], scale=2)
    fig.show()


def plot_networkx_colore(G1, G2, pos1, pos2, row_vals, col_vals, camera,
                         val_range=None, cbar_thk=20, cbar_len=0.4,
                         lab_name='graph', figsize=(700, 600), cmap='seismic', xval=0.8,
                         nlabel=True):
    """Plot the two networks with edge color specified
    Params:
    ------
    """
    if val_range is None:
        val_max = np.array([row_vals.max(), col_vals.max()]).max()
        val_min = np.array([row_vals.min(), col_vals.min()]).min()
    else:
        val_min, val_max = val_range
    print("max, min abs value in 1st and 2nd edge vals:", val_max, val_min)

    # Normalize + convert colormap
    colorscale = matplotlib_to_plotly_colorscale(cmap)

    # ----------------------------
    # Build plot traces

    # Nodes (same for both graphs)
    trace_nodes_G1 = node_trace(G1, pos1, label=nlabel)
    trace_nodes_G2 = node_trace(G2, pos2, nstart=len(G1.nodes()), label=nlabel)

    # Edges
    trace_edges_G1 = edge_trace_constant(G1, pos1, row_vals, cmap, vmin=val_min, vmax=val_max, width=10)
    trace_edges_G2 = edge_trace_constant(G2, pos2, col_vals, cmap, vmin=val_min, vmax=val_max, width=10)

    # Colorbar (based on G2 edge values)
    colorbar_trace = dummy_colorbar_trace(val_min, val_max, colorscale, xval=xval, thickness=cbar_thk, len=cbar_len)

    # ----------------------------
    # Assemble figure

    fig = go.Figure(data=[
        trace_nodes_G1,
        *trace_edges_G1,
        trace_nodes_G2,
        *trace_edges_G2,
        colorbar_trace
    ])

    axisFormat = dict(
                showbackground=False,
                showticklabels=False,
                autorange=True,
                showgrid=False,
        )


    fig.update_layout(
        # title="Graph Edge Visualization with Lam_gli Row/Column Sums",
        scene=dict(
            xaxis=dict(title='x'),
            yaxis=dict(title='y'),
            zaxis=dict(title='z'),
            aspectmode="data",
        ),
        showlegend=False,
        margin=dict(l=0, r=0, b=0, t=40),
        height=700
    )

    #set an appropriate camera
    camera = camera
    fig.update_layout(scene_camera=camera)

    pio.write_image(fig, lab_name+'.png', width=figsize[0], height=figsize[1], scale=2)
    fig.show()


def draw_sibigraph(G, weight_attr='weight', part0_c='#8a8a8a', part1_c='#2159d1',
                   figsize=(6, 4), figname='s', tol=1e-4, lw_fac=10., lab_diff=0.08):
    """Visualize a signed bipartite graph
    """
    # Get bipartite node sets
    part0 = [n for n, d in G.nodes(data=True) if d.get("bipartite", 0) == 0]
    part1 = [n for n, d in G.nodes(data=True) if d.get("bipartite", 0) == 1]

    # Arrange node positions: row 0 at y=1, row 1 at y=0
    pos = {}
    pos_lab = {}
    loc_diff = (len(part0) - len(part1))/2.
    for i, node in enumerate(part0):
        pos[node] = (i, 1)
        pos_lab[node] = (i, 1+lab_diff)
    for i, node in enumerate(part1):
        pos[node] = (i+loc_diff, 0)
        pos_lab[node] = (i+loc_diff, -lab_diff)

    # Separate edges by sign
    pos_edges = [(u, v) for u, v, d in G.edges(data=True) if d.get(weight_attr, 0) >= tol]
    neg_edges = [(u, v) for u, v, d in G.edges(data=True) if d.get(weight_attr, 0) <= -tol]

    # Edge widths
    edge_weights = nx.get_edge_attributes(G, weight_attr)
    pos_widths = [abs(edge_weights[e])*lw_fac for e in pos_edges]
    neg_widths = [abs(edge_weights[e])*lw_fac for e in neg_edges]

    # Draw nodes
    plt.figure(figsize=figsize)
    nx.draw_networkx_nodes(G, pos, nodelist=part0, node_color=part0_c, node_size=300)
    nx.draw_networkx_nodes(G, pos, nodelist=part1, node_color=part1_c, node_size=300)

    # Draw edges
    nx.draw_networkx_edges(G, pos, edgelist=pos_edges, edge_color='black', width=pos_widths)
    nx.draw_networkx_edges(G, pos, edgelist=neg_edges, edge_color='red', style='dashed', width=neg_widths)

    # Draw labels
    nx.draw_networkx_labels(G, pos_lab, font_size=10)

    # Turn off axis
    plt.axis('off')
    # plt.tight_layout()
    plt.savefig(figname+'-biG.png', dpi=300, bbox_inches='tight')
    plt.show()


def draw_sibigraph_nodec(G, nodec, weight_attr='weight', cmap_name='tab10',
                   figsize=(6, 4), figname='s', tol=1e-4, lw_fac=10., lab_diff=0.08):
    """Visualize a signed bipartite graph with node colors separated
    """
    from matplotlib import colormaps

    # Get bipartite node sets
    part0 = [n for n, d in G.nodes(data=True) if d.get("bipartite", 0) == 0]
    part1 = [n for n, d in G.nodes(data=True) if d.get("bipartite", 0) == 1]

    # Arrange node positions: row 0 at y=1, row 1 at y=0
    pos = {}
    pos_lab = {}
    loc_diff = (len(part0) - len(part1))/2.
    for i, node in enumerate(part0):
        pos[node] = (i, 1)
        pos_lab[node] = (i, 1+lab_diff)
    for i, node in enumerate(part1):
        pos[node] = (i+loc_diff, 0)
        pos_lab[node] = (i+loc_diff, -lab_diff)

    # Seperate node colors
    colors = set(nodec)
    cmap = colormaps[cmap_name]
    color_map = {cid: cmap(i / max(len(colors) - 1, 1)) for i, cid in enumerate(colors)}
    node_colors = [color_map[nodec[n]] for n in range(G.number_of_nodes())]

    # Separate edges by sign
    pos_edges = [(u, v) for u, v, d in G.edges(data=True) if d.get(weight_attr, 0) >= tol]
    neg_edges = [(u, v) for u, v, d in G.edges(data=True) if d.get(weight_attr, 0) <= -tol]

    # Edge widths
    edge_weights = nx.get_edge_attributes(G, weight_attr)
    pos_widths = [abs(edge_weights[e])*lw_fac for e in pos_edges]
    neg_widths = [abs(edge_weights[e])*lw_fac for e in neg_edges]

    # Draw nodes
    plt.figure(figsize=figsize)
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=300)

    # Draw edges
    nx.draw_networkx_edges(G, pos, edgelist=pos_edges, edge_color='black', width=pos_widths)
    nx.draw_networkx_edges(G, pos, edgelist=neg_edges, edge_color='red', style='dashed', width=neg_widths)

    # Draw labels
    nx.draw_networkx_labels(G, pos, font_size=10)

    # Turn off axis
    plt.axis('off')
    # plt.tight_layout()
    plt.savefig(figname+'-biG-cluster.png', dpi=300, bbox_inches='tight')
    plt.show()


def draw_sibigraph_node2c(G, nodec, weight_attr='weight', n0colors=['#b9d4d8', '#8a8a8a'], n1colors=['#1ce0e5', '#2159d1'],
                   figsize=(6, 4), figname='s', tol=1e-4, lw_fac=10., lab_diff=0.08): #'#f6f3f1', '#dccab6','#ffdcf5','#ffd7c6'
    """Visualize a signed bipartite graph with node colors separated
    Params:
    ------
    nodec, list of 0 or 1, 0 for reversing the label and 1 for remaining the label
    """
    from matplotlib import colormaps

    # Get bipartite node sets
    part0 = [n for n, d in G.nodes(data=True) if d.get("bipartite", 0) == 0]
    part1 = [n for n, d in G.nodes(data=True) if d.get("bipartite", 0) == 1]

    # Arrange node positions: row 0 at y=1, row 1 at y=0
    pos = {}
    pos_lab = {}
    loc_diff = (len(part0) - len(part1))/2.
    for i, node in enumerate(part0):
        pos[node] = (i, 1)
        pos_lab[node] = (i, 1+lab_diff)
    for i, node in enumerate(part1):
        pos[node] = (i+loc_diff, 0)
        pos_lab[node] = (i+loc_diff, -lab_diff)

    # Seperate node colors
    node_colors = []
    for i,node in enumerate(G.nodes()):
        if node in part0:
            node_colors.append(n0colors[nodec[i]])
        else:
            node_colors.append(n1colors[nodec[i]])

    # Separate edges by sign
    pos_edges = [(u, v) for u, v, d in G.edges(data=True) if d.get(weight_attr, 0) >= tol]
    neg_edges = [(u, v) for u, v, d in G.edges(data=True) if d.get(weight_attr, 0) <= -tol]

    # Edge widths
    edge_weights = nx.get_edge_attributes(G, weight_attr)
    pos_widths = [abs(edge_weights[e])*lw_fac for e in pos_edges]
    neg_widths = [abs(edge_weights[e])*lw_fac for e in neg_edges]

    # Draw nodes
    plt.figure(figsize=figsize)
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=300)

    # Draw edges
    nx.draw_networkx_edges(G, pos, edgelist=pos_edges, edge_color='black', width=pos_widths)
    nx.draw_networkx_edges(G, pos, edgelist=neg_edges, edge_color='red', style='dashed', width=neg_widths)

    # Draw labels
    nx.draw_networkx_labels(G, pos_lab, font_size=10)

    # Turn off axis
    plt.axis('off')
    # plt.tight_layout()
    plt.savefig(figname+'-biG-2cluster.png', dpi=300, bbox_inches='tight')
    plt.show()


def extract_positions(G):
    pos = nx.get_node_attributes(G, 'pos')  # Use 'pos' attribute if it exists
    if not pos:
        pos = {n: n for n in G.nodes()}
    return pos


def edge_trace_3d(G, pos, color, width):
    x, y, z = [], [], []
    for u, v in G.edges():
        x += [pos[u][0], pos[v][0], None]
        y += [pos[u][1], pos[v][1], None]
        z += [pos[u][2], pos[v][2], None]
    return go.Scatter3d(
        x=x, y=y, z=z,
        mode='lines',
        line=dict(color=color, width=width),
        hoverinfo='none',
        name='Edges'
    )


def node_trace_3d(G, pos, color, size):
    x, y, z = zip(*[pos[n] for n in G.nodes()])
    labels = [str(n) for n in G.nodes()]
    return go.Scatter3d(
        x=x, y=y, z=z,
        mode='markers',
        marker=dict(size=size, color=color),
        text=labels,
        textposition='top center',
        textfont=dict(size=12, color='black'),
        hoverinfo='text',
        name='Nodes'
    )
