import subprocess
import socket
import os

def start_server(path, ip):
    command1 = f'start cmd /K "cd {path}\\venv\\Scripts && activate.bat && cd {path}\\backend && py manage.py runserver {ip}:8000"'
    command2 = f'start cmd /K "cd {path}\\venv\\Scripts && activate.bat && cd {path}\\frontend && streamlit run do.py"'

    subprocess.Popen(command1, shell=True)
    subprocess.Popen(command2, shell=True)

if __name__ == "__main__":
    host = socket.gethostname()

    ip = socket.gethostbyname(host)
    path = os.getcwd()
    
    print()
    print(f"実行中のパス：{path}")
    print(f"実行中のIPv4アドレス：{ip}")
    print()

    start_server(path, ip)