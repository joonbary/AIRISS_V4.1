"""
Async helper utilities for cross-platform compatibility
"""
import asyncio
import sys
import logging
from typing import Callable, Any

logger = logging.getLogger(__name__)

async def run_sync_in_async(func: Callable, *args, **kwargs) -> Any:
    """
    Run a synchronous function in an async context safely.
    Works across different platforms (Windows, Linux, Railway).
    """
    try:
        # Try to get the current event loop
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            # No running loop, create a new one
            loop = asyncio.get_event_loop()
            if loop is None:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
        
        # Run the sync function in executor
        result = await loop.run_in_executor(None, func, *args)
        return result
        
    except Exception as e:
        logger.error(f"Error running sync function in async: {e}")
        # Fallback: try to run directly if possible
        try:
            return func(*args, **kwargs)
        except Exception as e2:
            logger.error(f"Fallback also failed: {e2}")
            raise e