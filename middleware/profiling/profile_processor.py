from opentelemetry.sdk.trace import SpanProcessor, ReadableSpan
from opentelemetry.trace import Span
from opentelemetry.context import Context
from collections import deque
from typing import Optional
import os
import sys
import time
import inspect
import json
from middleware.profiling import extract_stack, MAX_STACK_DEPTH, LRUCache  # Assuming utils.py is in the same directory


class ProfileSpanProcessor(SpanProcessor):
    def __init__(self, max_stack_depth=5):
        """
        Initialize the processor with a max stack depth.
        """
        self.cache = LRUCache(max_size=256)
        self.max_stack_depth = max_stack_depth

    def on_start(self, span: Span, parent_context: Optional[Context] = None) -> None:
        """
        Adds profiling data to the span attributes when the span starts.
        """
        # Extract the current frame from the active stack
        raw_frame = self._get_current_frame()

        if raw_frame is None:
            print("No frames found")
            return  # No frame available, skip

        # Use extract_stack to get the stack details
        cwd = os.getcwd()  # Current working directory for absolute paths
        stack_id, frame_ids, frames = extract_stack(raw_frame, self.cache, cwd, self.max_stack_depth)

        # Add profiling data to the span's context using the set_attribute method
        span.set_attribute("profiling.stack_id", str(stack_id))
        span.set_attribute("profiling.frames", json.dumps(frames))
        span.set_attribute("profiling.frame_ids", str(frame_ids))

    def on_end(self, span: ReadableSpan) -> None:
        """
        Called when the span ends. Send profiling data directly to Middleware.
        """
        try:
            # Capture the stack trace and other profiling information when the span ends.
            stack_sample = self._sample_stack()

            # Send profiling data directly to Middleware
            self._send_to_mw(span, stack_sample)

        except Exception as e:
            # Handle any exceptions
            Span.record_exception(e)

    def _sample_stack(self):
        """Capture the current stack trace."""
        cwd = os.getcwd()
        try:
            sample = [
                (str(tid), extract_stack(frame, self.cache, cwd))
                for tid, frame in sys._current_frames().items()
            ]
            return sample
        except Exception as e:
            print("exception:",e)
            # Span.record_exception(e)
            return []

    def _send_to_mw(self, span: ReadableSpan, stack_sample):
        """Send profiling data to Middleware."""
        timestamp = time.perf_counter()  # Get the current timestamp for profiling data
        
        # Create an envelope to hold profiling data
        envelope = {
            "timestamp": timestamp,
            "span_id": span.get_span_context().span_id,
            "stack_sample": stack_sample,
        }
        
        # Directly print or log the envelope (can be replaced with actual sending logic)
        # print(f"Captured profiling data: {envelope}")
        # You could replace this print statement with any logic to send this data to a monitoring system.

    def _get_current_frame(self):
        """
        Retrieves the current frame from the call stack and extracts useful information.
        """
        try:
            frame = inspect.currentframe()
            if frame:
            #     # Extract function name and line number for example
            #     function_name = frame.f_code.co_name
            #     line_number = frame.f_lineno
            #     return {"function": function_name, "line": line_number}
                return frame
            else:
                return None
        except Exception:
            return None

    def shutdown(self) -> None:
        # Cleanup actions if necessary
        pass

    def force_flush(self, timeout_millis: int = 30000) -> bool:
        # Used for forced flushes if required
        return True
