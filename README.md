# gemini-ensnarl

## Introduction
This repository contains code and analysis notebooks for **characterizing generalized ensnarlment of spatial networks** — quantifying and visualizing how embedded networks intertwine through one another via the incomplete Gauss linking integral and the corresponding operator. In particular, both the sign of the values and the absolute values are examined. 

This repository accompanies the article **"GEMINI: Generalized Ensnarlment Measure from
Incomplete-linkage of Network-network Interactions"** (Yu Tian, Chinmayi Subramanya,
Carl D. Modes, 2026), [arXiv:2606.05153](https://arxiv.org/abs/2606.05153).

## Repository layout

```
pygemini/                     Importable package — all reusable analysis code
  linking.py                 Incomplete Gauss linking integral between line segments
  signed.py                  Signed bipartite graph, signed biclustering analysis
  lattices.py                Synthetic lattice generators (periodic, ensnarled ladders)
  nulls.py                   Spatial, radius null models for the empirical networks
  regions.py                 Region extraction, graph building, component diagnostics
  viz_lattice.py             Plotting helpers for the synthetic-lattice notebook
  viz_data.py                Plotting helpers for the real-data notebook
notebooks/
  01_synthetic_lattices.ipynb   Analysis of synthetic ensnarled lattices
  02_real_data.ipynb            Analysis of the empirical spatial networks
data/                        Folder for real data
```

The two notebooks are thin **drivers**: every function they call is imported from the
`gemini_ensnarl` package, so the same analysis code is shared between them.

## Installation

**To use the package** (recommended for most users) — installs `gemini_ensnarl` and its
dependencies into your environment:

```bash
python -m venv .venv
source .venv/bin/activate
pip install git+https://github.com/yutian-research/EnsnarlNet.git
```

**To develop / modify the code** — clone the repository and do an *editable* install, so
your edits to `gemini_ensnarl/` take effect immediately:

```bash
git clone https://github.com/<your-account>/EnsnarlNet.git
cd EnsnarlNet
python -m venv .venv
source .venv/bin/activate
pip install -e .            # editable install
# for the exact published environment instead: pip install -r requirements.txt
```
`requirements.txt` pins the versions used for the published results.

## Reproducing the results

1. Install as above.
2. For the real-data notebook, obtain the input data and edit the `path` variable in the
   *"import data sets"* cell (see [`data/README.md`](data/README.md) for the expected
   schema and provenance). The data is obtained from the **VesselGraph** dataset (sample
   `CD1-E_no1`), with Allen Mouse Brain Atlas region annotations.
3. Run each notebook top to bottom:
   ```bash
   jupyter lab notebooks/01_synthetic_lattices.ipynb
   jupyter lab notebooks/02_real_data.ipynb
   ```
   The synthetic-lattice notebook needs no external data.


## Acknowledgements

The synthetic ensnarled ladder lattice geometries were originally produced with the `kirchhoff` / `goflow` packages by Felix Kramer (https://github.com/felixk1990). The lattice generators here have been rewritten as self-contained NetworkX builders (`pygemini/lattices.py`) that reproduce those geometries exactly, so that the package has no dependency on the original circuit machinery.

## Data source

The empirical networks derive from the VesselGraph dataset:

> Paetzold, J. C., et al. *Whole Brain Vessel Graphs: A Dataset and Benchmark for Graph
> Learning and Neuroscience (VesselGraph).* NeurIPS 2021 Datasets and Benchmarks.
> https://github.com/jocpae/VesselGraph

## Citation
If you use this code in your research, please consider citing our paper:

```
@article{tsm2026gemini,
  title={GEMINI: Generalized Ensnarlment Measure from Incomplete-linkage of Network-network Interactions},
  author={Yu Tian and Chinmayi Subramanya and Carl D. Modes},
  journal = {Preprint},
  volume = {},
  number = {},
  pages = {arXiv:2606.05153},
  year = {2026},
}
```
## Contact
If you have any questions, please contact [Yu Tian](mailto:yu.tian.research@gmail.com).
