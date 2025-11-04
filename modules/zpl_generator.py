"""
ZPL (Zebra Programming Language) Label Generator
Generates label code for Zebra thermal printers (ZD421)

Standard label size: 3" x 2" (203 DPI)
Label content: PO number, dimensions, window type, label numbering
"""

from datetime import datetime
from typing import Dict, Optional
from fractions import Fraction
from modules.fraction_utils import format_fraction


class ZPLGenerator:
    """Generate ZPL code for window labels"""

    def __init__(self, dpi: int = 203, label_width: float = 3.0, label_height: float = 2.0):
        """
        Initialize ZPL generator

        Args:
            dpi: Printer dots per inch (default 203 for ZD421)
            label_width: Label width in inches
            label_height: Label height in inches
        """
        self.dpi = dpi
        self.label_width = label_width
        self.label_height = label_height

        # Calculate dots from inches
        self.width_dots = int(label_width * dpi)
        self.height_dots = int(label_height * dpi)

    def generate_window_label(
        self,
        po_number: str,
        window_data: Dict,
        label_number: int,
        total_labels: int,
        order_date: Optional[datetime] = None
    ) -> str:
        """
        Generate ZPL code for a single window label

        Args:
            po_number: Purchase order number
            window_data: Dict with thickness, width, height, window_type
            label_number: Current label number (1, 2, 3...)
            total_labels: Total labels for this window spec
            order_date: Order date (optional)

        Returns:
            ZPL code string ready to send to printer
        """
        # Extract window data
        thickness = float(window_data.get('thickness', 0))
        width = float(window_data.get('width', 0))
        height = float(window_data.get('height', 0))
        window_type = window_data.get('window_type', 'Unknown')
        shape_notes = window_data.get('shape_notes', '')

        # Format dimensions as fractions
        thickness_str = self._format_dimension(thickness)
        width_str = self._format_dimension(width)
        height_str = self._format_dimension(height)
        dimensions = f"{thickness_str}\" x {width_str}\" x {height_str}\""

        # Format date
        date_str = order_date.strftime("%m/%d/%Y") if order_date else datetime.now().strftime("%m/%d/%Y")

        # Build ZPL code
        zpl = self._build_3x2_label(
            po_number=po_number,
            dimensions=dimensions,
            window_type=window_type,
            label_number=label_number,
            total_labels=total_labels,
            order_date=date_str,
            shape_notes=shape_notes
        )

        return zpl

    def _format_dimension(self, decimal_value: float) -> str:
        """
        Convert decimal dimension to fraction string

        Args:
            decimal_value: Decimal value (e.g., 1.5)

        Returns:
            Fraction string (e.g., "1 1/2")
        """
        try:
            frac = Fraction(decimal_value).limit_denominator(16)
            return format_fraction(frac)
        except:
            # Fallback to decimal if fraction conversion fails
            return f"{decimal_value:.2f}"

    def _build_3x2_label(
        self,
        po_number: str,
        dimensions: str,
        window_type: str,
        label_number: int,
        total_labels: int,
        order_date: str,
        shape_notes: str = ""
    ) -> str:
        """
        Build ZPL code for 3x2 inch label

        Layout:
        +---------------------------+
        | PO: 2024-11-001     1/4  |  <- PO number (large) and label count
        |---------------------------|
        | Rectangle                 |  <- Window type
        | 1 1/2" x 36" x 48"       |  <- Dimensions
        |---------------------------|
        | Date: 11/04/2024         |  <- Order date
        +---------------------------+

        Returns:
            ZPL code string
        """
        # ZPL formatting notes:
        # ^XA = Start label format
        # ^FO = Field Origin (x, y position)
        # ^A0 = Font (0=default), N=normal, height, width
        # ^FD = Field Data
        # ^FS = Field Separator
        # ^XZ = End label format
        # ^BY = Barcode field default (width, ratio, height)
        # ^BC = Code 128 barcode

        # Truncate long strings
        po_display = po_number[:20] if len(po_number) > 20 else po_number
        window_type_display = window_type[:25] if len(window_type) > 25 else window_type
        dimensions_display = dimensions[:30] if len(dimensions) > 30 else dimensions

        zpl = f"""^XA

^FO50,30^A0N,60,60^FDPO: {po_display}^FS
^FO480,30^A0N,40,40^FD{label_number}/{total_labels}^FS

^FO50,100^GB500,3,3^FS

^FO50,120^A0N,35,35^FD{window_type_display}^FS
^FO50,165^A0N,40,40^FD{dimensions_display}^FS

^FO50,230^GB500,3,3^FS

^FO50,250^A0N,25,25^FDDate: {order_date}^FS
"""

        # Add shape notes if custom shape
        if shape_notes and window_type.lower() in ['custom', 'custom shape']:
            notes_display = shape_notes[:30] if len(shape_notes) > 30 else shape_notes
            zpl += f"^FO50,285^A0N,20,20^FDNotes: {notes_display}^FS\n"

        # Optional: Add barcode of PO number for scanning
        # Uncomment to enable barcode
        # zpl += f"^FO50,320^BY2^BCN,60,Y,N,N^FD{po_number}^FS\n"

        zpl += "^XZ"

        return zpl

    def generate_preview_image_zpl(self, zpl_code: str) -> str:
        """
        Generate ZPL code that can be used for preview generation
        (Note: Actual preview rendering requires additional tools)

        Args:
            zpl_code: Original ZPL code

        Returns:
            Same ZPL code (placeholder for future preview feature)
        """
        # For now, return same ZPL
        # Future: Could integrate with labelary.com API or similar for preview
        return zpl_code

    def generate_batch_zpl(self, labels: list) -> str:
        """
        Generate ZPL for multiple labels (batch printing)

        Args:
            labels: List of dicts with label data

        Returns:
            Combined ZPL code for all labels
        """
        batch_zpl = ""
        for label_data in labels:
            zpl = self.generate_window_label(
                po_number=label_data.get('po_number', ''),
                window_data=label_data.get('window_data', {}),
                label_number=label_data.get('label_number', 1),
                total_labels=label_data.get('total_labels', 1),
                order_date=label_data.get('order_date')
            )
            batch_zpl += zpl + "\n\n"

        return batch_zpl

    def save_zpl_to_file(self, zpl_code: str, filename: str) -> str:
        """
        Save ZPL code to a .zpl file

        Args:
            zpl_code: ZPL code string
            filename: Output filename (without extension)

        Returns:
            Full path to saved file
        """
        import os

        # Ensure .zpl extension
        if not filename.endswith('.zpl'):
            filename += '.zpl'

        # Create labels directory if it doesn't exist
        output_dir = 'labels'
        os.makedirs(output_dir, exist_ok=True)

        filepath = os.path.join(output_dir, filename)

        with open(filepath, 'w') as f:
            f.write(zpl_code)

        return filepath


def test_generator():
    """Test the ZPL generator"""
    generator = ZPLGenerator()

    # Test data
    window_data = {
        'thickness': 1.5,
        'width': 36,
        'height': 48,
        'window_type': 'Rectangle',
        'shape_notes': ''
    }

    zpl = generator.generate_window_label(
        po_number='2024-11-001',
        window_data=window_data,
        label_number=1,
        total_labels=4,
        order_date=datetime.now()
    )

    print("Generated ZPL Code:")
    print("=" * 60)
    print(zpl)
    print("=" * 60)

    # Save to file
    filepath = generator.save_zpl_to_file(zpl, 'test_label')
    print(f"\nSaved to: {filepath}")


if __name__ == "__main__":
    test_generator()
