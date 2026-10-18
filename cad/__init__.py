"""Parametric pizza-oven CAD. Units are millimetres. Kernel is build123d.

Importing this package does not load the OpenCASCADE kernel. Geometry
modules do.
"""

from cad.parameters import DEFAULT_PARAMETERS, OvenParameters

__all__ = ["DEFAULT_PARAMETERS", "OvenParameters"]
