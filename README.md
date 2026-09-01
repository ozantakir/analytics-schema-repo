# Central Analytics Schema Repository

This repository is the **Single Source of Truth** for all analytics events.

## Key Principles
- **JSON Schema Rules:** Contains raw JSON schemas for every event tracked in production.
- **Multi-Destination Declarations:** Maps events to target platforms (`FIREBASE`, `ADJUST`, `INSIDER`, etc.).
- **Code Generation Engine:** Runs automated generator scripts to build target models whenever schemas update.

## CI/CD Pipeline Workflow
When a Pull Request is merged into `main`:
1. `generate_kotlin_events.py` runs automatically to output strongly-typed `EventModel` classes.
2. Automated GitHub Action opens Pull Request to the **https://github.com/ozantakir/AnalyticsAndroidExample** repositories with updated generated code.
