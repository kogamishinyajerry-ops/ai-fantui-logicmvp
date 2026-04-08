# Architecture

- `src/well_harness/controller.py`: confirmed deploy control truth.
- `src/well_harness/runner.py`: simulation loop composition.
- `src/well_harness/plant.py`: simplified deploy-side plant and sensor feedback.
- `src/well_harness/switches.py`: SW1 / SW2 interval-triggered latch behavior.
- `src/well_harness/demo.py`: deterministic demo-facing answer layer.
- `src/well_harness/demo_server.py`: local HTTP server and API shell.
- `src/well_harness/static/`: cockpit UI assets.
- `tools/`: validation and automation entrypoints.
