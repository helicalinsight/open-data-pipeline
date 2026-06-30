from .api import app
import os
import subprocess
import multiprocessing
ASKONDATA_PORT=os.getenv("ASKONDATA_PORT", 3001)

@app.shell_context_processor
def make_shell_context():
    return {"app": app}
def start_gunicorn():
    """Start Gunicorn server."""
    num_cores = multiprocessing.cpu_count()
    num_workers = (2 * num_cores) + 1
    gunicorn_cmd = [
        'gunicorn',
        '--reload',
        '-w', str(num_workers),            # Number of worker processes
        '-b', f'0.0.0.0:{ASKONDATA_PORT}', # Binding address and port
        '--timeout', '300',                # Timeout set to 5 minutes to allow run now to finish
        'src.api:app'         # Adjust this according to your module structure
    ]
    subprocess.run(gunicorn_cmd, check=True)

if __name__ == '__main__':
    if os.getenv("APP_ENVIRONMENT") == "prod":
        start_gunicorn()
    elif os.getenv("APP_ENVIRONMENT") == "dev":
        start_gunicorn()
    else:
        app.run(debug=True, host="0.0.0.0", port=ASKONDATA_PORT, threaded=True)
