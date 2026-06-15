# Data

Files used:

- `CD1-E-no1_iso3um_stitched_segmentation_bulge_size_3.0_atlas_processed.csv`
- `CD1-E-no1_iso3um_stitched_segmentation_bulge_size_3.0_nodes_processed.csv`
- `CD1-E-no1_iso3um_stitched_segmentation_bulge_size_3.0_edges_processed.csv`

## Provenance

These are obtained from the **VesselGraph** dataset, sample **`CD1-E_no1`** (the
"Preprocessed" version):

> Paetzold, J. C., et al. *Whole Brain Vessel Graphs: A Dataset and Benchmark for
> Graph Learning and Neuroscience (VesselGraph).* NeurIPS 2021 Datasets and Benchmarks.
> https://github.com/jocpae/VesselGraph


## Schema

**Atlas** (`*_atlas_processed.csv`, `sep=';'`):

Each row corresponds to a node, and each column corresponds to an Allen atlas region (the column names are in the format of `Region_Acronym_[Acronym]`, where `[Acronym]` contains three characters)


**Nodes** (`*_nodes_processed.csv`, `sep=';'`):

| column             | type  | description                                  |
|--------------------|-------|----------------------------------------------|
| `id`               | int   | unique node id                               |
| `pos_x`, `pos_y`, `pos_z` | float | spatial coordinates                   |
| `degree`           | int   | node degree                                  |
| `isAtSampleBorder` | bool/0-1 | whether the node lies on the sample boundary |


**Edges** (`*_edges_processed.csv`, `sep=';'`):

| column                  | type  | description                                 |
|-------------------------|-------|---------------------------------------------|
| `id`                    | int   | unique edge id                              |
| `node1id`, `node2id`    | int   | endpoint node ids                           |
| `minRadiusAvg`, `minRadiusStd` | float | minimal-radius statistics            |
| `hasNodeAtSampleBorder` | bool/0-1 | whether an endpoint is on the sample border |

(The edges file additionally carries the full VesselGraph geometry metrics —
`length`, `distance`, `curveness`, `volume`, `avgCrossSection`, `avgRadius*`,
`maxRadius*`, `roundness*`, `node1_degree`, `node2_degree`, `num_voxels`.)
