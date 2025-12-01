"""
Function name detection utilities.

Provides utilities for detecting the name of calling functions,
useful for SDK monitoring and analytics.
"""

import inspect
from typing import Optional


def get_caller_function_name(skip_frames: int = 1) -> Optional[str]:
    """
    Get the name of the calling function.

    Uses inspect.currentframe() to walk up the call stack and find
    the function name. This is useful for SDK monitoring where we need
    to track which SDK function is being called.

    Args:
        skip_frames: Number of frames to skip (default: 1 for direct caller)
                    Increase if you need to skip wrapper functions.

    Returns:
        Function name or None if detection fails

    Note:
        - This function may not work in all contexts (C extensions, etc.)
        - Performance impact is minimal but should be used judiciously
        - Frame references are properly cleaned up to prevent memory leaks

    Example:
        >>> def my_function():
        ...     name = get_caller_function_name()
        ...     print(name)  # Will print the name of the function that called my_function
        >>>
        >>> def caller():
        ...     my_function()  # my_function will detect "caller"
    """
    frame = inspect.currentframe()
    try:
        # Skip the current frame (this function)
        for _ in range(skip_frames + 1):
            if frame is None:
                return None
            frame = frame.f_back

        if frame is None:
            return None

        return frame.f_code.co_name
    finally:
        # Important: delete frame reference to prevent reference cycles
        # This helps Python's garbage collector clean up properly
        del frame
