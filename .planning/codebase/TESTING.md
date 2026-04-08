# Testing

Primary regression command:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -p 'test_*.py'
```

Useful contract validators:

```bash
PYTHONPATH=src python3 tools/validate_debug_json_schema.py --format json
PYTHONPATH=src python3 tools/validate_demo_answer_schema.py --format json
PYTHONPATH=src python3 tools/validate_validation_report_schema.py --format json
PYTHONPATH=src python3 tools/validate_validation_schema_runner_report_schema.py --format json
PYTHONPATH=src python3 tools/validate_validation_schema_checker_report_schema.py --format json
```
