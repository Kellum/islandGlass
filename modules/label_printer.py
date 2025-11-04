"""
Label Printer Module
Handles communication with Zebra thermal printers via network connection

Supports:
- Network printing (TCP/IP)
- Mock printing for development
- File output (.zpl files)
- Connection testing
- Print queue management
"""

import socket
import os
from datetime import datetime
from typing import Optional, Tuple
from enum import Enum


class PrinterStatus(Enum):
    """Printer status codes"""
    ONLINE = "online"
    OFFLINE = "offline"
    ERROR = "error"
    UNKNOWN = "unknown"


class LabelPrinter:
    """Handle Zebra printer communication"""

    def __init__(
        self,
        ip_address: str = "192.168.1.100",
        port: int = 9100,
        timeout: int = 5,
        mock_mode: bool = True
    ):
        """
        Initialize label printer

        Args:
            ip_address: Printer IP address
            port: Printer port (default 9100 for Zebra)
            timeout: Connection timeout in seconds
            mock_mode: If True, saves to file instead of printing
        """
        self.ip_address = ip_address
        self.port = port
        self.timeout = timeout
        self.mock_mode = mock_mode
        self.last_error = None

    def print_label(self, zpl_code: str, filename: Optional[str] = None) -> Tuple[bool, str]:
        """
        Print a single label

        Args:
            zpl_code: ZPL code string
            filename: Optional filename for mock mode

        Returns:
            Tuple of (success: bool, message: str)
        """
        if self.mock_mode:
            return self._mock_print(zpl_code, filename)
        else:
            return self._network_print(zpl_code)

    def print_batch(self, zpl_codes: list, base_filename: Optional[str] = None) -> Tuple[bool, str]:
        """
        Print multiple labels

        Args:
            zpl_codes: List of ZPL code strings
            base_filename: Base filename for mock mode

        Returns:
            Tuple of (success: bool, message: str)
        """
        if not zpl_codes:
            return False, "No labels to print"

        if self.mock_mode:
            return self._mock_batch_print(zpl_codes, base_filename)
        else:
            return self._network_batch_print(zpl_codes)

    def test_connection(self) -> Tuple[bool, str]:
        """
        Test printer connection

        Returns:
            Tuple of (connected: bool, message: str)
        """
        if self.mock_mode:
            return True, "Mock mode - connection test skipped"

        try:
            # Try to connect to printer
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            sock.connect((self.ip_address, self.port))

            # Send status request (Zebra specific)
            # ~HS = Host Status request
            sock.sendall(b"~HS\n")

            # Receive response
            response = sock.recv(1024)
            sock.close()

            if response:
                return True, f"Printer online at {self.ip_address}:{self.port}"
            else:
                return False, "Printer did not respond"

        except socket.timeout:
            self.last_error = "Connection timeout"
            return False, f"Connection timeout to {self.ip_address}:{self.port}"

        except socket.error as e:
            self.last_error = str(e)
            return False, f"Connection error: {str(e)}"

        except Exception as e:
            self.last_error = str(e)
            return False, f"Unexpected error: {str(e)}"

    def get_status(self) -> PrinterStatus:
        """
        Get printer status

        Returns:
            PrinterStatus enum
        """
        if self.mock_mode:
            return PrinterStatus.ONLINE

        connected, _ = self.test_connection()
        return PrinterStatus.ONLINE if connected else PrinterStatus.OFFLINE

    def _network_print(self, zpl_code: str) -> Tuple[bool, str]:
        """
        Send ZPL code to printer via network

        Args:
            zpl_code: ZPL code string

        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            # Create socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)

            # Connect to printer
            sock.connect((self.ip_address, self.port))

            # Send ZPL code
            sock.sendall(zpl_code.encode('utf-8'))

            # Close connection
            sock.close()

            return True, f"Label sent to printer at {self.ip_address}"

        except socket.timeout:
            self.last_error = "Print timeout"
            return False, "Print operation timed out"

        except socket.error as e:
            self.last_error = str(e)
            return False, f"Network error: {str(e)}"

        except Exception as e:
            self.last_error = str(e)
            return False, f"Print error: {str(e)}"

    def _network_batch_print(self, zpl_codes: list) -> Tuple[bool, str]:
        """
        Send multiple ZPL codes to printer

        Args:
            zpl_codes: List of ZPL code strings

        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            # Create socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)

            # Connect to printer
            sock.connect((self.ip_address, self.port))

            # Send all ZPL codes
            for zpl_code in zpl_codes:
                sock.sendall(zpl_code.encode('utf-8'))
                sock.sendall(b'\n\n')  # Separator between labels

            # Close connection
            sock.close()

            return True, f"Batch of {len(zpl_codes)} labels sent to printer"

        except Exception as e:
            self.last_error = str(e)
            return False, f"Batch print error: {str(e)}"

    def _mock_print(self, zpl_code: str, filename: Optional[str] = None) -> Tuple[bool, str]:
        """
        Save ZPL code to file instead of printing (for development)

        Args:
            zpl_code: ZPL code string
            filename: Output filename

        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            # Create output directory
            output_dir = 'labels_output'
            os.makedirs(output_dir, exist_ok=True)

            # Generate filename if not provided
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"label_{timestamp}.zpl"
            elif not filename.endswith('.zpl'):
                filename += '.zpl'

            filepath = os.path.join(output_dir, filename)

            # Save ZPL to file
            with open(filepath, 'w') as f:
                f.write(zpl_code)

            return True, f"Mock print: Saved to {filepath}"

        except Exception as e:
            self.last_error = str(e)
            return False, f"Mock print error: {str(e)}"

    def _mock_batch_print(self, zpl_codes: list, base_filename: Optional[str] = None) -> Tuple[bool, str]:
        """
        Save multiple ZPL codes to files (mock batch print)

        Args:
            zpl_codes: List of ZPL code strings
            base_filename: Base filename for output files

        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            # Create output directory
            output_dir = 'labels_output'
            os.makedirs(output_dir, exist_ok=True)

            # Generate base filename if not provided
            if not base_filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                base_filename = f"batch_{timestamp}"

            saved_files = []

            # Save each label
            for i, zpl_code in enumerate(zpl_codes, 1):
                filename = f"{base_filename}_label{i:03d}.zpl"
                filepath = os.path.join(output_dir, filename)

                with open(filepath, 'w') as f:
                    f.write(zpl_code)

                saved_files.append(filename)

            return True, f"Mock print: Saved {len(saved_files)} labels to {output_dir}/"

        except Exception as e:
            self.last_error = str(e)
            return False, f"Mock batch print error: {str(e)}"

    def set_mock_mode(self, enabled: bool):
        """Enable or disable mock printing mode"""
        self.mock_mode = enabled

    def get_last_error(self) -> Optional[str]:
        """Get last error message"""
        return self.last_error


def test_printer():
    """Test the label printer"""
    # Create printer in mock mode
    printer = LabelPrinter(mock_mode=True)

    # Test ZPL code
    test_zpl = """^XA
^FO50,30^A0N,60,60^FDPO: TEST-001^FS
^FO480,30^A0N,40,40^FD1/1^FS
^FO50,100^GB500,3,3^FS
^FO50,120^A0N,35,35^FDRectangle^FS
^FO50,165^A0N,40,40^FD1 1/2" x 36" x 48"^FS
^FO50,230^GB500,3,3^FS
^FO50,250^A0N,25,25^FDDate: 11/04/2024^FS
^XZ"""

    # Test single print
    success, message = printer.print_label(test_zpl, "test_label")
    print(f"Single print: {message}")

    # Test batch print
    zpl_codes = [test_zpl for _ in range(3)]
    success, message = printer.print_batch(zpl_codes, "test_batch")
    print(f"Batch print: {message}")

    # Test connection (mock mode)
    connected, message = printer.test_connection()
    print(f"Connection test: {message}")

    # Test status
    status = printer.get_status()
    print(f"Printer status: {status.value}")


if __name__ == "__main__":
    test_printer()
