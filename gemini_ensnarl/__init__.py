"""gemini_ensnarl: generalized ensnarlment analysis of spatial networks.

Reusable analysis code for the synthetic-lattice and real-data notebooks.
Visualization helpers live in :mod:`gemini_ensnarl.viz_lattice` and
:mod:`gemini_ensnarl.viz_data` (imported explicitly, as they are notebook-specific).
"""

from .linking import Gauss_linking_integral
from .signed import (
    build_sibigraph,
    critical_flip_angles,
    candidate_mid_angles,
    sign_patterns_from_angles,
)
from .lattices import generate_periodic_lattices, generate_ladder_lattices

__all__ = [
    "Gauss_linking_integral",
    "build_sibigraph",
    "critical_flip_angles",
    "candidate_mid_angles",
    "sign_patterns_from_angles",
    "generate_periodic_lattices",
    "generate_ladder_lattices",
]

__version__ = "0.1.0"
