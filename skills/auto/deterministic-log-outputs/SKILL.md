---
name: deterministic-log-outputs
description: Use when extracting, normalizing, or summarizing logs into structured output.
---
- Inspect the required output schema and log formats before changing parsing or serialization code.
- Normalize service identifiers and other categorical fields exactly as specified, applying transformations consistently.
- Preserve required timestamps and fields; represent absent values using the schema's prescribed null or omission behavior.
- Sort output explicitly by every required key, with a defined ascending or descending direction.
- Emit required schema-version and generator metadata at the correct level of the output object.
- Validate the serialized result by parsing it and checking its schema, normalized values, and sort order.