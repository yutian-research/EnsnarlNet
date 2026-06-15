"""Plotly/matplotlib visualization helpers for the real-data notebook."""

import numpy as np
import networkx as nx
import plotly.graph_objects as go
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
            marker=dict(size=size, color=color, opacity=0.8),
            text=[str(n+nstart) for n in G.nodes()],
            textposition='top center',
            hoverinfo='text'
        )
    else:
        return go.Scatter3d(
            x=x, y=y, z=z,
            mode='markers',
            marker=dict(size=size, color=color, opacity=0.8),
            text=[str(n+nstart) for n in G.nodes()],
            textposition='top center',
            hoverinfo='text'
        )


def node_trace_nolabel(G, pos, color='#3f3f40', size=8):
    x, y, z = zip(*[pos[n] for n in G.nodes()])
    return go.Scatter3d(
        x=x, y=y, z=z,
        mode='markers',
        marker=dict(size=size, color=color, opacity=0.8),
        # text=[str(n+nstart) for n in G.nodes()],
        # textposition='top center',
        # hoverinfo='text'
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


def edge_trace_constant(G, pos, values, color_scale, vrange=None, width=8):
    """Edge trace with edge colors (from values)."""
    if vrange is not None:
        vmin, vmax = vrange
    else:
        vmin, vmax = np.min(values), np.max(values)

    edge_list = list(G.edges())
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


def dummy_colorbar_trace(vmin, vmax, colorscale, xval=0.8, thickness=10, len=0.4, tk_fz=18):
    return go.Scatter3d(
        x=[None], y=[None], z=[None],
        mode='markers',
        marker=dict(
            size=0.1,
            color=[vmin, vmax],
            colorscale=colorscale,
            cmin=vmin,
            cmax=vmax,
            showscale=True,
            colorbar=dict(
                # title='|Column Sum|',
                titleside='right',
                thickness=20,
                len=len,
                x=xval,
                tickfont=dict(size=tk_fz)
            )
        ),
        showlegend=False,
        hoverinfo='none'
    )


def plot_networkx_12label(G1, G2, pos1, pos2, row_c='#8a8a8a', col_c='#2159d1',
                          width=10, camera=None, savefig=False, figname='', figsize=[1100,700], scale=2):
    """Plot the two networks with edge color specified
    Params:
    ------
    """

    # ----------------------------
    # Build plot traces

    # Nodes (same for both graphs)
    trace_nodes_G1 = node_trace(G1, pos1)
    trace_nodes_G2 = node_trace(G2, pos2, nstart=len(G1.nodes()))

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
        margin=dict(l=0, r=0, b=0, t=40),
        height=700
    )

    if camera:
        fig.update_layout(scene_camera=camera)
    if savefig:
        fig.write_image(figname+'.png', width=figsize[0], height=figsize[1], scale=scale)
    fig.show()


def plot_networkx_12nolabel(G1, G2, pos1, pos2, row_c='#8a8a8a', col_c='#2159d1', size=8, width=10,
                            camera=None, savefig=False, figname='', figsize=[1100,700],
                            scale=2, ticklabel=False, ax_fz=30):
    """Plot the two networks with edge color specified
    Params:
    ------
    """

    # ----------------------------
    # Build plot traces

    # Nodes (same for both graphs)
    trace_nodes_G1 = node_trace_nolabel(G1, pos1, size=size)
    trace_nodes_G2 = node_trace_nolabel(G2, pos2, size=size)

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

    if ticklabel:
        scene_dict = dict(
            xaxis=dict(title=dict(text="x", font=dict(size=ax_fz))),
            yaxis=dict(title=dict(text="y", font=dict(size=ax_fz))),
            zaxis=dict(title=dict(text="z", font=dict(size=ax_fz))),
            aspectmode="data",
        )
    else:
        scene_dict = dict(
            xaxis=dict(title=dict(text="x", font=dict(size=ax_fz)), showticklabels=False),
            yaxis=dict(title=dict(text="y", font=dict(size=ax_fz)), showticklabels=False),
            zaxis=dict(title=dict(text="z", font=dict(size=ax_fz)), showticklabels=False),
            aspectmode="data",
        )
    fig.update_layout(
        # title="Graph Edge Visualization with Lam_gli Row/Column Sums",
        scene=scene_dict,
        showlegend=False,
        margin=dict(l=0, r=0, b=0, t=0), # this is to make the figure tight; can add more to "t" if need a title
        height=700
    )
    if camera:
        fig.update_layout(scene_camera=camera)
    if savefig:
        fig.write_image(figname+'.png', width=figsize[0], height=figsize[1], scale=scale)
    fig.show()


def plot_networkx_color1e(G1, pos1, row_sums,
                         cmap='coolwarm', xval=0.8, ns=2, lw=2):
    """Plot the two networks with edge color specified
    Params:
    ------
    """
    val_max = np.array(row_sums).max()
    val_min = np.array(row_sums).min()
    print("max, min abs value in edge vals:", val_max, val_min)

    # Normalize + convert colormap
    colorscale = matplotlib_to_plotly_colorscale(cmap)

    # ----------------------------
    # Build plot traces

    # Nodes (same for both graphs)
    trace_nodes_G1 = node_trace(G1, pos1, size=ns, label=False)
    # trace_nodes_G2 = node_trace(G2, pos2, size=ns, label=False)

    # Edges
    trace_edges_G1 = edge_trace_constant(G1, pos1, row_sums, cmap, width=10)
    # trace_edges_G2 = edge_trace_constant(G2, pos2, col_sums, cmap, width=10)

    # Colorbar (based on G2 edge values)
    colorbar_trace = dummy_colorbar_trace(val_min, val_max, colorscale, xval=xval)

    # ----------------------------
    # Assemble figure

    fig = go.Figure(data=[
        trace_nodes_G1,
        *trace_edges_G1,
        # trace_nodes_G2,
        # *trace_edges_G2,
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

    fig.show()


def plot_networkx_colore(G1, G2, pos1, pos2, row_sums, col_sums, cmap='coolwarm', val_range=None, xval=0.8, ns=2, lw=2,
                         camera=None, savefig=False, figname='', figsize=[1100,700], scale=2,
                         ticklabel=False, ax_fz=30, cbar_len=0.4):
    """Plot the two networks with edge color specified
    Params:
    ------
    """
    val_max = np.array([row_sums.max(), col_sums.max()]).max()
    val_min = np.array([row_sums.min(), col_sums.min()]).min()
    print("max, min abs value in 1st and 2nd edge vals:", val_max, val_min)
    if val_range is not None:
        val_min, val_max = val_range
    print("max, min in cmap:", val_max, val_min)

    # Normalize + convert colormap
    colorscale = matplotlib_to_plotly_colorscale(cmap)

    # ----------------------------
    # Build plot traces

    # Nodes (same for both graphs)
    trace_nodes_G1 = node_trace(G1, pos1, size=ns, label=False)
    trace_nodes_G2 = node_trace(G2, pos2, size=ns, label=False)

    # Edges
    trace_edges_G1 = edge_trace_constant(G1, pos1, row_sums, cmap, vrange=[val_min, val_max], width=lw)
    trace_edges_G2 = edge_trace_constant(G2, pos2, col_sums, cmap, vrange=[val_min, val_max], width=lw)

    # Colorbar (based on G2 edge values)
    colorbar_trace = dummy_colorbar_trace(val_min, val_max, colorscale, xval=xval, len=cbar_len)

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

    if ticklabel:
        scene_dict = dict(
            xaxis=dict(title=dict(text="x", font=dict(size=ax_fz))),
            yaxis=dict(title=dict(text="y", font=dict(size=ax_fz))),
            zaxis=dict(title=dict(text="z", font=dict(size=ax_fz))),
            aspectmode="data",
        )
    else:
        scene_dict = dict(
            xaxis=dict(title=dict(text="x", font=dict(size=ax_fz)), showticklabels=False),
            yaxis=dict(title=dict(text="y", font=dict(size=ax_fz)), showticklabels=False),
            zaxis=dict(title=dict(text="z", font=dict(size=ax_fz)), showticklabels=False),
            aspectmode="data",
        )

    fig.update_layout(
        # title="Graph Edge Visualization with Lam_gli Row/Column Sums",
        scene=scene_dict,
        showlegend=False,
        margin=dict(l=0, r=0, b=0, t=0),
        height=700
    )
    if camera:
        fig.update_layout(scene_camera=camera)
    if savefig:
        fig.write_image(figname+'.png', width=figsize[0], height=figsize[1], scale=scale)
    fig.show()


def build_edge_traces(G, color, width=2, name=None):
    traces = []

    for u, v in G.edges():
        x0, y0, z0 = G.nodes[u]["pos"]
        x1, y1, z1 = G.nodes[v]["pos"]

        traces.append(
            go.Scatter3d(
                x=[x0, x1],
                y=[y0, y1],
                z=[z0, z1],
                mode="lines",
                line=dict(color=color, width=width),
                hoverinfo="none",
                name=name,
                showlegend=False
            )
        )
    return traces


def build_highlight_traces(G, edge_list, color, width=6, name=None):
    traces = []

    for u, v in edge_list:
        if not G.has_edge(u, v):
            continue

        x0, y0, z0 = G.nodes[u]["pos"]
        x1, y1, z1 = G.nodes[v]["pos"]

        traces.append(
            go.Scatter3d(
                x=[x0, x1],
                y=[y0, y1],
                z=[z0, z1],
                mode="lines",
                line=dict(color=color, width=width),
                hoverinfo="none",
                name=name,
                showlegend=False
            )
        )
    return traces


def plot_networkx_colore_sel(G_all, G1, G2, edge_sel1, edge_sel2,
                             ns=3, lw=5, camera=None, savefig=False, figname='', figsize=[1100,700], scale=2):
    """plot edges with selected ones highlighted
    """
    # plot the nodes
    xs, ys, zs = [], [], []
    for n in G_all.nodes():
        x, y, z = G_all.nodes[n]["pos"]
        xs.append(x)
        ys.append(y)
        zs.append(z)

    node_trace = go.Scatter3d(
        x=xs,
        y=ys,
        z=zs,
        mode="markers",
        marker=dict(size=ns, color='#3f3f40'),
        name="Nodes",
        showlegend=True
    )

    # Base subgraphs
    traces_G1 = build_edge_traces(G1, color="lightblue",  width=lw)
    traces_G2 = build_edge_traces(G2, color="pink", width=lw)

    # Emphasized edges
    traces_G1_sel = build_highlight_traces(G1, edge_sel1, color="darkblue", width=lw)
    traces_G2_sel = build_highlight_traces(G2, edge_sel2, color="darkred", width=lw) #[edges2[i] for i in edges_neg[1]]

    fig = go.Figure(data=[node_trace, *traces_G1, *traces_G2, *traces_G1_sel, *traces_G2_sel])

    # axisFormat = dict(
    #                 showbackground=True,
    #                 showticklabels=True,
    #                 autorange=True,
    #                 showgrid=True,
    #         )

    fig.update_layout(
        # title="Overlay of G1 and G2 with Highlighted Edges",
        scene=dict(
            xaxis=dict(title="x", showbackground=True),
            yaxis=dict(title="y", showbackground=True),
            zaxis=dict(title="z", showbackground=True),
            aspectmode="data",
        ),
        showlegend=False,
        margin=dict(l=0, r=0, t=50, b=0),
        height=700
    )

    if camera:
        fig.update_layout(scene_camera=camera)
    if savefig:
        fig.write_image(figname+'.png', width=figsize[0], height=figsize[1], scale=scale)

    fig.show()


def plot_networkx_2colore_sel(G_all, G1, G2, edge_sel11, edge_sel21, edge_sel12, edge_sel22,
                              colorset = [["lightblue", "pink"],["#636EFA", "magenta"], ["darkblue", "darkred"]],
                             ns=3, lw=5, camera=None, savefig=False, figname='',
                              figsize=[1100,700], scale=2, ticklabel=False, ax_fz=30):
    """plot edges with selected ones highlighted: one strong, one internediate
    """
    # plot the nodes
    xs, ys, zs = [], [], []
    for n in G_all.nodes():
        x, y, z = G_all.nodes[n]["pos"]
        xs.append(x)
        ys.append(y)
        zs.append(z)

    node_trace = go.Scatter3d(
        x=xs,
        y=ys,
        z=zs,
        mode="markers",
        marker=dict(size=ns, color='#3f3f40'),
        name="Nodes",
        showlegend=True
    )

    # Base subgraphs
    traces_G1 = build_edge_traces(G1, color=colorset[0][0],  width=lw)
    traces_G2 = build_edge_traces(G2, color=colorset[0][1], width=lw)

    # Emphasized edges - 1
    traces_G1_sel1 = build_highlight_traces(G1, edge_sel11, color=colorset[2][0], width=lw)
    traces_G2_sel1 = build_highlight_traces(G2, edge_sel21, color=colorset[2][1], width=lw) #[edges2[i] for i in edges_neg[1]]

    # Emphasized edges - 2
    traces_G1_sel2 = build_highlight_traces(G1, edge_sel12, color=colorset[1][0], width=lw)
    traces_G2_sel2 = build_highlight_traces(G2, edge_sel22, color=colorset[1][1], width=lw)

    fig = go.Figure(data=[node_trace, *traces_G1, *traces_G2, *traces_G1_sel2,
                          *traces_G2_sel2, *traces_G1_sel1, *traces_G2_sel1])

    # axisFormat = dict(
    #                 showbackground=True,
    #                 showticklabels=True,
    #                 autorange=True,
    #                 showgrid=True,
    #         )

    if ticklabel:
        scene_dict = dict(
            xaxis=dict(title=dict(text="x", font=dict(size=ax_fz))),
            yaxis=dict(title=dict(text="y", font=dict(size=ax_fz))),
            zaxis=dict(title=dict(text="z", font=dict(size=ax_fz))),
            aspectmode="data",
        )
    else:
        scene_dict = dict(
            xaxis=dict(title=dict(text="x", font=dict(size=ax_fz)), showticklabels=False),
            yaxis=dict(title=dict(text="y", font=dict(size=ax_fz)), showticklabels=False),
            zaxis=dict(title=dict(text="z", font=dict(size=ax_fz)), showticklabels=False),
            aspectmode="data",
        )


    fig.update_layout(
        # title="Overlay of G1 and G2 with Highlighted Edges",
        scene=scene_dict,
        showlegend=False,
        margin=dict(l=0, r=0, t=0, b=0),
        height=700
    )

    if camera:
        fig.update_layout(scene_camera=camera)
    if savefig:
        fig.write_image(figname+'.png', width=figsize[0], height=figsize[1], scale=scale)

    fig.show()


def draw_sibigraph(G, weight_attr='weight', part0_c='#8a8a8a', part1_c='#2159d1',
                   figsize=(6, 4), figname='s', tol=1e-4, node_size=200, lw_fac=10., labels=True):
    """Visualize a signed bipartite graph
    """
    # Get bipartite node sets
    part0 = [n for n, d in G.nodes(data=True) if d.get("bipartite", 0) == 0]
    part1 = [n for n, d in G.nodes(data=True) if d.get("bipartite", 0) == 1]

    # Arrange node positions: row 0 at y=1, row 1 at y=0
    pos = {}
    loc_diff = (len(part0) - len(part1))/2.
    for i, node in enumerate(part0):
        pos[node] = (i, 1)
    for i, node in enumerate(part1):
        pos[node] = (i+loc_diff, 0)

    # Separate edges by sign
    pos_edges = [(u, v) for u, v, d in G.edges(data=True) if d.get(weight_attr, 0) >= tol]
    neg_edges = [(u, v) for u, v, d in G.edges(data=True) if d.get(weight_attr, 0) <= -tol]

    # Edge widths
    edge_weights = nx.get_edge_attributes(G, weight_attr)
    pos_widths = [abs(edge_weights[e])*lw_fac for e in pos_edges]
    neg_widths = [abs(edge_weights[e])*lw_fac for e in neg_edges]

    # Draw nodes
    plt.figure(figsize=figsize)
    nx.draw_networkx_nodes(G, pos, nodelist=part0, node_color=part0_c, node_size=node_size)
    nx.draw_networkx_nodes(G, pos, nodelist=part1, node_color=part1_c, node_size=node_size)

    # Draw edges
    nx.draw_networkx_edges(G, pos, edgelist=pos_edges, edge_color='black', width=pos_widths)
    nx.draw_networkx_edges(G, pos, edgelist=neg_edges, edge_color='red', style='dashed', width=neg_widths)

    # Draw labels
    if labels:
        nx.draw_networkx_labels(G, pos, font_size=10)

    # Turn off axis
    plt.axis('off')
    # plt.tight_layout()
    plt.savefig(figname+'-biG.png', dpi=300, bbox_inches='tight')
    plt.show()


def draw_sibigraph_nodec(G, nodec, weight_attr='weight', cmap_name='tab10',
                   figsize=(6, 4), figname='s', tol=1e-4, lw_fac=10., labels=True):
    """Visualize a signed bipartite graph with node colors separated
    """
    from matplotlib import colormaps

    # Get bipartite node sets
    part0 = [n for n, d in G.nodes(data=True) if d.get("bipartite", 0) == 0]
    part1 = [n for n, d in G.nodes(data=True) if d.get("bipartite", 0) == 1]

    # Arrange node positions: row 0 at y=1, row 1 at y=0
    pos = {}
    loc_diff = (len(part0) - len(part1))/2.
    for i, node in enumerate(part0):
        pos[node] = (i, 1)
    for i, node in enumerate(part1):
        pos[node] = (i+loc_diff, 0)

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
    if labels:
        nx.draw_networkx_labels(G, pos, font_size=10)

    # Turn off axis
    plt.axis('off')
    # plt.tight_layout()
    plt.savefig(figname+'-biG-cluster.png', dpi=300, bbox_inches='tight')
    plt.show()
