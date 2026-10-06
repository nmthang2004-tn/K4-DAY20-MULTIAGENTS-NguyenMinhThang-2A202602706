---
name: verified-data-deliverables
description: Use when a task transforms source data into specified files or structured analysis outputs.
---
- Inspect the input data, task requirements, and workspace layout before processing.
- Create every required deliverable at its designated location; do not treat a written summary as a substitute for an output file.
- Match required headers, field order, data types, and serialization format exactly.
- Apply deduplication and missing-value rules explicitly, and verify row counts against those rules.
- Normalize categories and timestamps to the required canonical forms; make timezone conversions explicit.
- Represent money in the requested unit and numeric type, avoiding floating-point conversion when exact minor units are required.
- Include required metadata separately from data rows and preserve the specified output schema.
- Reopen and parse each generated artifact, then check its path, schema, and key values before finishing.