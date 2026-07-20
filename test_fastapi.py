import subprocess
import time


def run():
    # Start server in background
    p = subprocess.Popen(["venv/bin/python", "main.py"])
    time.sleep(2)
    try:
        # Run event bus test
        subprocess.run(["venv/bin/python", "event_bus_example.py"])
    finally:
        p.terminate()


if __name__ == "__main__":
    run()
