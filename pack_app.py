import os
import shutil
import subprocess


def pack_application():
    # Create a temporary directory to store the packaged application
    dist_dir = os.path.join(os.getcwd(), 'dist_temp')
    os.makedirs(dist_dir, exist_ok=True)

    try:
        # Copy necessary files and directories to the temporary directory
        shutil.copytree('venv', os.path.join(dist_dir, 'venv'))
        for filename in ['cpu_chart_widget.py', 'cpu_watcher.py', 'database_widget.py', 'monitor_cli.py',
                         'monitor_ui.py', 'process_management_widget.py', 'settings_widget.py', 'settings.json']:
            shutil.copy(filename, dist_dir)

        # Run PyInstaller to package the application
        subprocess.run(['pyinstaller', '--onefile', '--clean', '--distpath', 'dist', 'monitor_ui.py'],
                       cwd=dist_dir, check=True)
    finally:
        # Clean up temporary directory
        shutil.rmtree(dist_dir)


if __name__ == "__main__":
    pack_application()
