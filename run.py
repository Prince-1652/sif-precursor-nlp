import subprocess
import re
import time
import os

def kill_process_on_port(port):
    print(f"Checking for processes listening on port {port}...")
    try:
        # Run netstat to find PIDs listening on the port
        output = subprocess.check_output(f"netstat -ano | findstr :{port}", shell=True).decode()
        pids = set()
        for line in output.strip().split('\n'):
            if 'LISTENING' in line:
                parts = re.split(r'\s+', line.strip())
                if len(parts) >= 5:
                    pid = parts[-1]
                    if pid != '0':
                        pids.add(pid)
        
        if not pids:
            print(f"No listening processes found on port {port}.")
            return

        for pid in pids:
            print(f"Killing process {pid} on port {port}...")
            subprocess.run(f"taskkill /F /PID {pid}", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(1) # Give the OS a moment to free the port completely
            
    except subprocess.CalledProcessError:
        print(f"No process found on port {port}.")
    except Exception as e:
        print(f"Error checking port {port}: {e}")

def main():
    # Default ports
    backend_port = 8000
    frontend_port = 3000
    
    # 1. Kill any existing processes on these ports to free them up
    kill_process_on_port(backend_port)
    kill_process_on_port(frontend_port)
    
    # 2. Get the base project path
    base_path = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.join(base_path, "backend")
    frontend_dir = os.path.join(base_path, "frontend")
    
    print("\nStarting Backend (Port 8000)...")
    # Using 'start cmd /k' to open a new terminal window that stays open
    backend_cmd = f'start cmd /k "cd /d "{backend_dir}" && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"'
    subprocess.Popen(backend_cmd, shell=True)
    
    print("Starting Frontend (Port 3000)...")
    frontend_cmd = f'start cmd /k "cd /d "{frontend_dir}" && npm run dev"'
    subprocess.Popen(frontend_cmd, shell=True)
    
    print("\nBoth services are starting up in separate windows!")
    print("Close those new terminal windows to stop the services.")

if __name__ == "__main__":
    main()
