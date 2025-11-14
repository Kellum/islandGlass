"""
Backend utilities for Island Glass CRM
"""
from .po_generator import generate_po_number, POGenerationError

__all__ = ['generate_po_number', 'POGenerationError']
