# Performance Monitoring Application

## Description
The Performance Monitoring Application is a Python-based tool designed to monitor and analyze system performance metrics. It provides a graphical user interface (GUI) for visualizing CPU workload, system events, and process management details. Additionally, it includes a command-line interface (CLI) for users who prefer interacting with the application via the terminal.

## Architecture
The application follows a modular architecture, consisting of several components:
- **CPU Chart Widget:** Displays CPU workload data in a graphical chart format.
- **CPU Watcher:** Monitors CPU usage and workload in real-time.
- **Database Widget:** Manages data storage and retrieval using an SQLite database.
- **Monitor CLI:** Provides a command-line interface for interacting with the application.
- **Monitor UI:** Graphical user interface for viewing and analyzing system performance metrics.
- **Process Management Widget:** Allows users to view and manage running processes on the system.
- **Settings Widget:** Configures application settings and preferences.

## Use Cases
- **System Monitoring:** Users can monitor CPU usage, workload, and system events in real-time
- **Data Analysis:** Provides tools for analyzing historical performance data stored in the database
- **Customization:** Users can customize application settings and preferences according to their needs

## Installation
* Download portable python archive from the [official Python website](https://www.python.org/ftp/python/3.10.10/python-3.10.10-embed-amd64.zip)
* Unpack the archive
* Unpack the contents of the repository into the same directory
* Create virtual environment: `./python.exe -m venv venv` (here and further assume PS shell)
* Activate the virtual environment: `./venv/Scripts/activate.ps1`
* Install dependencies: `./python.exe -m pip install -r requirements.txt`
* Run the application: `./python.exe ./monitor_ui.py`

## Dependencies
- PyQt5: Python binding for the Qt framework, used for building the GUI.
- psutil: Provides cross-platform functions for retrieving system information and monitoring processes.
- matplotlib: Library for creating static, animated, and interactive visualizations in Python.

## Database

SQLite database is used for storing performance data. 
The database schema consists of the following tables:

* **CpuWorkload:** Stores CPU usage data
* **SystemEvents:** Stores system events and notifications (was not used so far)

Example of record in CpuWorkload table:
```
| ID | Timestamp           | PID | ProcessName | Workload |
|----|---------------------|-----------|----------|----------|
| 1  | 2023-10-10 10:10:10 | 12345     | symantec.exe   | 0.5      |
```

The analysis of performance data can be done using SQL queries.
