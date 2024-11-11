import opentelemetry.trace as trace
from opentelemetry.sdk.trace import ReadableSpan, Span, SpanProcessor
import inspect
from typing import Optional
from opentelemetry.context import Context
import sys
# Custom Span Processor to inject surrounding code into spans
class SurroundingCodeSpanProcessor(SpanProcessor):
    def __init__(self):
        pass
    def on_start(
        self, span: Span, parent_context: Optional[Context] = None
    ) -> None:
        # Get the stack trace
        stack = inspect.stack()

        # Get the current Python version dynamically
        python_version = sys.version_info
        python_version_str = f"python{python_version[0]}.{python_version[1]}"

        # Initialize the surrounding code to be an empty string
        surrounding_code = []

        # Traverse the stack from deepest to shallowest to find the invocation location
        for frame_info in reversed(stack):
            filename = frame_info.filename

            # Skip frames from system libraries or internal packages (e.g., threading, http.server, etc.)
            # Dynamically check for 'site-packages', 'dist-packages', and current Python version path
            if python_version_str not in filename and 'site-packages' not in filename and 'dist-packages' not in filename:
                calling_frame = frame_info
                break
        else:
            # If no user application code is found, use the first available frame
            calling_frame = stack[0]

        # Extract details of the frame where the span is invoked
        frame = calling_frame.frame
        file_name = calling_frame.filename
        line_number = calling_frame.lineno

        # Try to get the surrounding code (10 lines before and after)
        try:
            with open(file_name, "r") as file:
                lines = file.readlines()

            # Ensure we don't go out of bounds when extracting the surrounding lines
            start_line = max(0, line_number - 6)  # 5 lines before the invocation line
            end_line = line_number + 4  # 5 lines after the invocation line

            surrounding_code = lines[start_line:end_line]
        except Exception as e:
            surrounding_code = [f"Could not retrieve source: {str(e)}"]

        # Format the surrounding code block
        codeblock = "\n".join([f"{i + start_line + 1}: {line.strip()}" for i, line in enumerate(surrounding_code)])

        # Add the surrounding code block to the span's attributes
        span.set_attribute("code.surrounding", f"path = {file_name} at line {line_number}\ncodeblock = {codeblock}")
    def on_end(self, span: ReadableSpan) -> None:
        # You can process the span before exporting here if needed
        pass

    def shutdown(self) -> None:
        # Called when the processor is shut down
        pass

    def force_flush(self, timeout_millis: int) -> bool:
        # If you need to flush spans manually, implement here
        pass


# # Initialize tracer provider with the custom span processor
# from opentelemetry.sdk.trace import TracerProvider
# from opentelemetry.sdk.trace.export import SimpleSpanProcessor

# # Initialize the tracer provider
# tracer_provider = TracerProvider()

# # Add the custom span processor
# span_processor = SurroundingCodeSpanProcessor()
# tracer_provider.add_span_processor(SimpleSpanProcessor(span_processor))

# # Set the global tracer provider
# trace.set_tracer_provider(tracer_provider)

# # Initialize a tracer
# tracer = trace.get_tracer(__name__)

# # Example function to trigger the span
# def capture_surrounding_code():
#     # Create a span and add the surrounding code as a single attribute
#     with tracer.start_as_current_span("example_span") as span:
#         span.set_attribute("example.key", "example value")
        
#         # Example logic
#         print("This is the example function")
#         return "Done"

# # Call the function to trigger the span creation
# capture_surrounding_code()
