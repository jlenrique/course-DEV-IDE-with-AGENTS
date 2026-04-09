# Reflection: L1-course-structure-snapshot — Attempt 2

## What Failed
The run failed with an invalid URL because Canvas environment keys were not loaded into process environment for woodshed execution.

## Root Cause Analysis
`reproduce_exemplar.py` lacked `.env` hydration, so `CANVAS_API_URL` was empty when `CanvasClient` initialized.

## Predicted Improvement
Load `{project-root}/.env` key-value pairs before running API calls in woodshed reproduction.

## Spec Changes
No exemplar spec changes were needed.

## Confidence Level
High
