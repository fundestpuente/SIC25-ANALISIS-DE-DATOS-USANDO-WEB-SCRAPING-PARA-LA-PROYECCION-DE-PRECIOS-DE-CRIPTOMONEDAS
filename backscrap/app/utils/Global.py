"""Utility helpers for API responses, console logging, and dev-only image dumps.

This module keeps the original behavior intact:
- ResponseUtil builds CustomResponse objects with the same status codes:
  * success  -> status=2
  * warning  -> status=3
  * error    -> status=4
- Console respects the DEV_MODE flag for printing logs and saving images.
- Paths and side effects (prints, image write) remain unchanged.

"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

import cv2  # OpenCV is required for image saving in dev mode
import os

from backscrap.app.pojo.models.modelos import CustomResponse
from backscrap.app.utils.config import DEV_MODE


class ResponseUtil:
    """Factory for standardized API responses (logic preserved)."""

    @staticmethod
    def success(message: str = "Operation completed successfully.", data: Optional[dict] = None) -> CustomResponse:
        """Return a success response wrapper with status=2.

        Args:
            message: Human-friendly message to include in the response.
            data: Optional payload; defaults to an empty dict if None.

        Returns:
            CustomResponse: Response with status=2, message, and data.
        """
        return CustomResponse(status=2, message=message, data=data or {})

    @staticmethod
    def error(message: str = "An error occurred.", data: Optional[dict] = None) -> CustomResponse:
        """Return an error response wrapper with status=4.

        Args:
            message: Human-friendly error message.
            data: Optional payload; defaults to an empty dict if None.

        Returns:
            CustomResponse: Response with status=4, message, and data.
        """
        return CustomResponse(status=4, message=message, data=data or {})

    @staticmethod
    def warning(message: str = "User not registered.", data: Optional[dict] = None) -> CustomResponse:
        """Return a warning response wrapper with status=3.

        Args:
            message: Human-friendly warning message.
            data: Optional payload; defaults to an empty dict if None.

        Returns:
            CustomResponse: Response with status=3, message, and data.
        """
        return CustomResponse(status=3, message=message, data=data or {})


class Console:
    """Lightweight console helper that respects DEV_MODE (logic preserved)."""

    # Keep a module-level dev flag that can be toggled at runtime.
    dev_mode: bool = DEV_MODE

    @staticmethod
    def isDevMode() -> bool:
        """Tell whether the application is running in developer mode.

        Returns:
            bool: True if DEV_MODE is enabled, False otherwise.
        """
        # Do not change the original return path.
        return Console.dev_mode

    @staticmethod
    def set_dev_mode(value: bool) -> None:
        """Set the developer mode flag at runtime.

        Args:
            value: Boolean flag to enable/disable dev mode.
        """
        Console.dev_mode = value

    @staticmethod
    def log(*msg: object) -> None:
        """Print arbitrary messages when in dev mode."""
        if Console.isDevMode():
            print(*msg)

    @staticmethod
    def table(data: Any) -> None:
        """Pretty-print lists/dicts in dev mode; fallback to str() for others.

        Args:
            data: Any object; lists/dicts are pretty-printed.
        """
        if Console.isDevMode():
            if isinstance(data, (list, dict)):
                from pprint import pprint  # local import to keep overhead minimal
                pprint(data)
            else:
                print(data)

    @staticmethod
    def warn(*msg: object) -> None:
        """Print a WARNING line in dev mode."""
        if Console.isDevMode():
            print(f"WARNING: {' '.join(map(str, msg))}")

    @staticmethod
    def error(*msg: object) -> None:
        """Print an ERROR line in dev mode."""
        if Console.isDevMode():
            print(f"ERROR: {' '.join(map(str, msg))}")

    @staticmethod
    def saveImg(folder: str, face: Any) -> None:
        """Save an image to ./assets/<folder>/face_<microseconds>.jpg in dev mode.

        This preserves the original I/O logic:
        - Uses the current working directory.
        - Creates the target folder if missing.
        - Writes the image using OpenCV's `imwrite`.
        - Prints the resulting file path.

        Args:
            folder: Subfolder name under ./assets/ where the image will be saved.
            face:   Image matrix (e.g., NumPy ndarray in OpenCV format).
        """
        if Console.isDevMode():
            output_dir = os.path.join(os.getcwd(), "assets", folder)
            os.makedirs(output_dir, exist_ok=True)

            file_name = f"face_{datetime.now().microsecond}.jpg"
            file_path = os.path.join(output_dir, file_name)

            cv2.imwrite(file_path, face)

            print(f"Image saved at: {file_path}")
