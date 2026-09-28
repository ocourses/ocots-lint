"""Vérification des conventions de rédaction ocots sur des sources LaTeX."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("ocots-lint")
except PackageNotFoundError:  # exécuté depuis les sources, sans installation
    __version__ = "0+inconnue"
