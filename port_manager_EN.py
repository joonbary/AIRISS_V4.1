#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AIRISS v4.1 Port Management Utility (English)
Tool to find available ports and run AIRISS
"""

import socket
import subprocess
import sys
import os
import time
from typing import List, Optional

def check_port_available(port: int) -> bool:
    """Check if port is available"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(1)
            result = sock.connect_ex(('localhost', port))
            return result != 0  # Connection failed = port available
    except Exception:
        return False

def find_available_ports(start_port: int = 8002, count: int = 10) -> List[int]:
    """Find list of available ports"""
    available_ports = []
    for port in range(start_port, start_port + count):
        if check_port_available(port):
            available_ports.append(port)
    return available_ports

def kill_process_on_port(port: int) -> bool:
    """Kill process using specific port (Windows)"""
    try:
        # Find process using port with netstat
        result = subprocess.run(
            ['netstat', '-ano'], 
            capture_output=True, 
            text=True, 
            encoding='utf-8'
        )
        
        lines = result.stdout.split('\n')
        pids_to_kill = []
        
        for line in lines:
            if f':{port}' in line and 'LISTENING' in line:
                parts = line.split()
                if len(parts) >= 5:
                    pid = parts[-1]
                    if pid.isdigit():
                        pids_to_kill.append(pid)
        
        # Kill processes
        killed = False
        for pid in pids_to_kill:
            try:
                subprocess.run(['taskkill', '/PID', pid, '/F'], 
                             capture_output=True, check=True)
                print(f"Successfully killed process PID {pid}")
                killed = True
            except subprocess.CalledProcessError:
                print(f"Failed to kill process PID {pid}")
        
        return killed
        
    except Exception as e:
        print(f"Error while killing process: {e}")
        return False

def run_airiss_on_port(port: int) -> None:
    """Run AIRISS on specified port"""
    print(f"\nStarting AIRISS v4.1 on port {port}...")
    print(f"Access URL: http://localhost:{port}")
    print(f"Stop server: Ctrl+C")
    print("-" * 50)
    
    # Set environment variable
    env = os.environ.copy()
    env['SERVER_PORT'] = str(port)
    
    try:
        # Run AIRISS
        subprocess.run([sys.executable, '-m', 'app.main'], env=env)
    except KeyboardInterrupt:
        print(f"\nAIRISS server stopped on port {port}")
    except Exception as e:
        print(f"\nError running AIRISS: {e}")

def main():
    """Main function"""
    print("AIRISS v4.1 Port Management Utility")
    print("=" * 50)
    
    # Check default port 8002
    default_port = 8002
    print(f"\nChecking default port {default_port} status...")
    
    if check_port_available(default_port):
        print(f"Port {default_port} is available!")
        
        # Ask if run immediately
        response = input(f"\nStart AIRISS on port {default_port}? (Y/n): ")
        if response.lower() != 'n':
            run_airiss_on_port(default_port)
            return
    else:
        print(f"Port {default_port} is in use")
        
        # Ask if kill process
        response = input(f"\nKill process using port {default_port}? (y/N): ")
        if response.lower() == 'y':
            if kill_process_on_port(default_port):
                print(f"\nWaiting...")
                time.sleep(3)
                
                if check_port_available(default_port):
                    print(f"Port {default_port} released successfully!")
                    run_airiss_on_port(default_port)
                    return
                else:
                    print(f"Port {default_port} still in use")
    
    # Find alternative ports
    print(f"\nSearching for alternative ports...")
    available_ports = find_available_ports(8003, 10)
    
    if not available_ports:
        print("No available ports found.")
        print("Try different port range or restart system.")
        return
    
    print(f"Available ports: {available_ports[:5]}")
    
    # Run on first available port
    selected_port = available_ports[0]
    print(f"\nSelected port {selected_port}.")
    
    response = input(f"Start AIRISS on port {selected_port}? (Y/n): ")
    if response.lower() != 'n':
        run_airiss_on_port(selected_port)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        print("Try running as administrator or check network settings.")
