# DLT Directory Structure

This directory contains the DLT (Data Load Tool) infrastructure:

- `dlt_data/` - Data and logs storage for DLT operations
- `dlt_state/` - State management for each schedule (isolated per schedule_id)
- `logs/` - Additional logging directory

These directories are mounted as volumes in Docker containers for DLT CDC operations.
