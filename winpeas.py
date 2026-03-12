#!/usr/bin/env python3
"""
WinPEAS - Windows Privilege Escalation Awesome Script
Python implementation for Windows privilege escalation enumeration
"""

import os
import sys
import subprocess
import json
import re
import winreg
import platform
from datetime import datetime
from pathlib import Path

class Colors:
    """ANSI color codes for output formatting"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

class WinPEAS:
    def __init__(self):
        self.results = {}
        self.start_time = datetime.now()
        
    def print_banner(self):
        """Print WinPEAS banner"""
        banner = f"""
{Colors.CYAN}{Colors.BOLD}
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║  ██╗    ██╗██╗███╗   ██╗██████╗ ███████╗ ██████╗ ███████╗ █████╗ ███████╗      ║
║  ██║    ██║██║████╗  ██║██╔══██╗██╔════╝██╔═══██╗██╔════╝██╔══██╗██╔════╝      ║
║  ██║ █╗ ██║██║██╔██╗ ██║██████╔╝█████╗  ██║   ██║███████╗███████║███████╗      ║
║  ██║███╗██║██║██║╚██╗██║██╔═══╝ ██╔══╝  ██║   ██║╚════██║██╔══██║╚════██║      ║
║  ╚███╔███╔╝██║██║ ╚████║██║     ███████╗╚██████╔╝███████║██║  ██║███████║      ║
║   ╚══╝╚══╝ ╚═╝╚═╝  ╚═══╝╚═╝     ╚══════╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝╚══════╝      ║
║                                                                              ║
║                    Windows Privilege Escalation Awesome Script              ║
║                              Python Edition                                  ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
{Colors.END}
"""
        print(banner)
        print(f"{Colors.GREEN}[+] Starting WinPEAS at {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}{Colors.END}\n")

    def run_command(self, command, timeout=30):
        """Run a command and return its output"""
        try:
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True, 
                timeout=timeout,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            return result.stdout.strip(), result.stderr.strip(), result.returncode
        except subprocess.TimeoutExpired:
            return "", "Command timed out", 1
        except Exception as e:
            return "", str(e), 1

    def print_section(self, title, color=Colors.CYAN):
        """Print a section header"""
        print(f"\n{color}{Colors.BOLD}{'='*80}{Colors.END}")
        print(f"{color}{Colors.BOLD}{title.center(80)}{Colors.END}")
        print(f"{color}{Colors.BOLD}{'='*80}{Colors.END}")

    def print_info(self, info, color=Colors.WHITE):
        """Print information with color"""
        print(f"{color}{info}{Colors.END}")

    def print_warning(self, warning):
        """Print warning in yellow"""
        print(f"{Colors.YELLOW}[!] {warning}{Colors.END}")

    def print_critical(self, critical):
        """Print critical finding in red"""
        print(f"{Colors.RED}[CRITICAL] {critical}{Colors.END}")

    def print_success(self, success):
        """Print success in green"""
        print(f"{Colors.GREEN}[+] {success}{Colors.END}")

    def system_info(self):
        """Gather basic system information"""
        self.print_section("SYSTEM INFORMATION")
        
        # OS Information
        self.print_info(f"OS: {platform.system()} {platform.release()}")
        self.print_info(f"Architecture: {platform.architecture()[0]}")
        self.print_info(f"Machine: {platform.machine()}")
        self.print_info(f"Processor: {platform.processor()}")
        
        # Current user
        self.print_info(f"Current User: {os.getenv('USERNAME', 'unknown')}")
        self.print_info(f"User Domain: {os.getenv('USERDOMAIN', 'unknown')}")
        self.print_info(f"Computer Name: {os.getenv('COMPUTERNAME', 'unknown')}")
        
        # System directory
        self.print_info(f"System Directory: {os.getenv('SYSTEMROOT', 'unknown')}")

    def registry_enumeration(self):
        """Enumerate Windows Registry for privilege escalation vectors"""
        self.print_section("REGISTRY ENUMERATION")
        
        # Interesting registry keys
        interesting_keys = [
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce"),
            (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"),
            (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon"),
        ]
        
        for hkey, subkey in interesting_keys:
            try:
                with winreg.OpenKey(hkey, subkey) as key:
                    self.print_info(f"Registry Key: {subkey}")
                    i = 0
                    while True:
                        try:
                            name, value, _ = winreg.EnumValue(key, i)
                            self.print_info(f"  {name}: {value}")
                            i += 1
                        except OSError:
                            break
            except Exception as e:
                self.print_warning(f"Could not access {subkey}: {e}")

    def services_enumeration(self):
        """Enumerate Windows services"""
        self.print_section("SERVICES ENUMERATION")
        
        # Get services using sc command
        stdout, stderr, rc = self.run_command("sc query state= all")
        if rc == 0:
            self.print_info("Windows Services:")
            for line in stdout.split('\n'):
                if 'SERVICE_NAME:' in line or 'DISPLAY_NAME:' in line:
                    self.print_info(f"  {line.strip()}")
        
        # Get service permissions
        self.print_info("\nChecking service permissions...")
        stdout, stderr, rc = self.run_command("sc sdshow Spooler 2>nul")
        if rc == 0 and stdout:
            self.print_info(f"Spooler service permissions: {stdout}")

    def processes_enumeration(self):
        """Enumerate running processes"""
        self.print_section("PROCESSES ENUMERATION")
        
        # Get running processes
        stdout, stderr, rc = self.run_command("tasklist /fo csv")
        if rc == 0:
            self.print_info("Running processes (first 20):")
            lines = stdout.split('\n')[:21]  # Header + 20 processes
            for line in lines:
                self.print_info(f"  {line}")
        
        # Get processes running as SYSTEM
        self.print_info("\nProcesses running as SYSTEM:")
        stdout, stderr, rc = self.run_command("tasklist /svc /fo csv | findstr SYSTEM")
        if rc == 0 and stdout:
            for line in stdout.split('\n'):
                if line.strip():
                    self.print_info(f"  {line}")

    def network_enumeration(self):
        """Enumerate network information"""
        self.print_section("NETWORK ENUMERATION")
        
        # Network interfaces
        stdout, stderr, rc = self.run_command("ipconfig /all")
        if rc == 0:
            self.print_info("Network Configuration:")
            for line in stdout.split('\n'):
                if line.strip():
                    self.print_info(f"  {line}")
        
        # Listening ports
        self.print_info("\nListening ports:")
        stdout, stderr, rc = self.run_command("netstat -an")
        if rc == 0:
            self.print_info("Network connections:")
            for line in stdout.split('\n')[:20]:  # First 20 lines
                if line.strip():
                    self.print_info(f"  {line}")

    def file_permissions(self):
        """Check file permissions and interesting files"""
        self.print_section("FILE PERMISSIONS")
        
        # Check for interesting directories
        interesting_dirs = [
            r"C:\Program Files",
            r"C:\Program Files (x86)",
            r"C:\Windows\System32",
            r"C:\Users",
            r"C:\Temp",
            r"C:\tmp"
        ]
        
        for directory in interesting_dirs:
            if os.path.exists(directory):
                self.print_info(f"Directory: {directory}")
                try:
                    stdout, stderr, rc = self.run_command(f'icacls "{directory}"')
                    if rc == 0:
                        for line in stdout.split('\n')[:5]:  # First 5 lines
                            self.print_info(f"  {line}")
                except:
                    pass

    def scheduled_tasks(self):
        """Enumerate scheduled tasks"""
        self.print_section("SCHEDULED TASKS")
        
        # Get scheduled tasks
        stdout, stderr, rc = self.run_command("schtasks /query /fo csv")
        if rc == 0:
            self.print_info("Scheduled Tasks:")
            lines = stdout.split('\n')[:10]  # First 10 tasks
            for line in lines:
                if line.strip():
                    self.print_info(f"  {line}")

    def user_enumeration(self):
        """Enumerate users and groups"""
        self.print_section("USER ENUMERATION")
        
        # Get local users
        stdout, stderr, rc = self.run_command("net user")
        if rc == 0:
            self.print_info("Local Users:")
            for line in stdout.split('\n'):
                if line.strip():
                    self.print_info(f"  {line}")
        
        # Get local groups
        self.print_info("\nLocal Groups:")
        stdout, stderr, rc = self.run_command("net localgroup")
        if rc == 0:
            for line in stdout.split('\n'):
                if line.strip():
                    self.print_info(f"  {line}")
        
        # Get current user groups
        self.print_info("\nCurrent User Groups:")
        stdout, stderr, rc = self.run_command("whoami /groups")
        if rc == 0:
            for line in stdout.split('\n'):
                if line.strip():
                    self.print_info(f"  {line}")

    def installed_software(self):
        """Enumerate installed software"""
        self.print_section("INSTALLED SOFTWARE")
        
        # Get installed programs
        stdout, stderr, rc = self.run_command('wmic product get name,version /format:csv')
        if rc == 0:
            self.print_info("Installed Software:")
            lines = stdout.split('\n')[:20]  # First 20 programs
            for line in lines:
                if line.strip() and 'Name' not in line:
                    self.print_info(f"  {line}")

    def environment_variables(self):
        """Check environment variables"""
        self.print_section("ENVIRONMENT VARIABLES")
        
        # Interesting environment variables
        interesting_vars = [
            'PATH', 'PATHEXT', 'TEMP', 'TMP', 'USERPROFILE', 
            'APPDATA', 'LOCALAPPDATA', 'PROGRAMFILES', 'PROGRAMFILES(X86)'
        ]
        
        for var in interesting_vars:
            value = os.getenv(var)
            if value:
                self.print_info(f"{var}: {value}")

    def run_all_checks(self):
        """Run all privilege escalation checks"""
        self.print_banner()
        
        try:
            self.system_info()
            self.registry_enumeration()
            self.services_enumeration()
            self.processes_enumeration()
            self.network_enumeration()
            self.file_permissions()
            self.scheduled_tasks()
            self.user_enumeration()
            self.installed_software()
            self.environment_variables()
            
        except KeyboardInterrupt:
            self.print_warning("\nScan interrupted by user")
        except Exception as e:
            self.print_critical(f"Error during scan: {e}")
        
        end_time = datetime.now()
        duration = end_time - self.start_time
        self.print_section("SCAN COMPLETE")
        self.print_success(f"Scan completed in {duration.total_seconds():.2f} seconds")
        self.print_info("Review the output above for potential privilege escalation vectors")

def main():
    """Main function"""
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help']:
        print("WinPEAS - Windows Privilege Escalation Awesome Script")
        print("Usage: python3 winpeas.py")
        print("No arguments required - just run the script")
        sys.exit(0)
    
    # Check if running on Windows
    if os.name != 'nt':
        print("This script is designed for Windows systems only.")
        sys.exit(1)
    
    winpeas = WinPEAS()
    winpeas.run_all_checks()

if __name__ == "__main__":
    main()
