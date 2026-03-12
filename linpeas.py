#!/usr/bin/env python3
"""
LinPEAS - Linux Privilege Escalation Awesome Script
Python implementation for privilege escalation enumeration
"""

import os
import sys
import subprocess
import json
import re
import stat
import pwd
import grp
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

class LinPEAS:
    def __init__(self):
        self.results = {}
        self.start_time = datetime.now()
        
    def print_banner(self):
        """Print LinPEAS banner"""
        banner = f"""
{Colors.CYAN}{Colors.BOLD}
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║  ██╗     ██╗███╗   ██╗██████╗ ███████╗ ██████╗ ███████╗ █████╗ ███████╗      ║
║  ██║     ██║████╗  ██║██╔══██╗██╔════╝██╔═══██╗██╔════╝██╔══██╗██╔════╝      ║
║  ██║     ██║██╔██╗ ██║██████╔╝█████╗  ██║   ██║███████╗███████║███████╗      ║
║  ██║     ██║██║╚██╗██║██╔═══╝ ██╔══╝  ██║   ██║╚════██║██╔══██║╚════██║      ║
║  ███████╗██║██║ ╚████║██║     ███████╗╚██████╔╝███████║██║  ██║███████║      ║
║  ╚══════╝╚═╝╚═╝  ╚═══╝╚═╝     ╚══════╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝╚══════╝      ║
║                                                                              ║
║                    Linux Privilege Escalation Awesome Script                ║
║                              Python Edition                                  ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
{Colors.END}
"""
        print(banner)
        print(f"{Colors.GREEN}[+] Starting LinPEAS at {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}{Colors.END}\n")

    def run_command(self, command, timeout=30):
        """Run a command and return its output"""
        try:
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True, 
                timeout=timeout
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
        try:
            with open('/etc/os-release', 'r') as f:
                os_info = f.read()
            self.print_info("OS Information:")
            for line in os_info.split('\n'):
                if line.strip():
                    self.print_info(f"  {line}")
        except:
            self.print_warning("Could not read /etc/os-release")
        
        # Kernel information
        stdout, stderr, rc = self.run_command("uname -a")
        if rc == 0:
            self.print_info(f"Kernel: {stdout}")
        
        # Architecture
        stdout, stderr, rc = self.run_command("arch")
        if rc == 0:
            self.print_info(f"Architecture: {stdout}")
        
        # Current user
        self.print_info(f"Current User: {os.getenv('USER', 'unknown')}")
        self.print_info(f"User ID: {os.getuid()}")
        self.print_info(f"Group ID: {os.getgid()}")
        
        # Hostname
        stdout, stderr, rc = self.run_command("hostname")
        if rc == 0:
            self.print_info(f"Hostname: {stdout}")

    def file_permissions(self):
        """Check for interesting file permissions"""
        self.print_section("FILE PERMISSIONS")
        
        # World-writable files
        self.print_info("Checking for world-writable files...")
        stdout, stderr, rc = self.run_command("find / -type f -perm -002 2>/dev/null | head -20")
        if stdout:
            self.print_warning("World-writable files found:")
            for line in stdout.split('\n'):
                if line.strip():
                    self.print_info(f"  {line}")
        
        # SUID files
        self.print_info("\nChecking for SUID files...")
        stdout, stderr, rc = self.run_command("find / -type f -perm -4000 2>/dev/null | head -20")
        if stdout:
            self.print_warning("SUID files found:")
            for line in stdout.split('\n'):
                if line.strip():
                    self.print_info(f"  {line}")
        
        # SGID files
        self.print_info("\nChecking for SGID files...")
        stdout, stderr, rc = self.run_command("find / -type f -perm -2000 2>/dev/null | head -20")
        if stdout:
            self.print_warning("SGID files found:")
            for line in stdout.split('\n'):
                if line.strip():
                    self.print_info(f"  {line}")

    def processes_services(self):
        """Check running processes and services"""
        self.print_section("PROCESSES AND SERVICES")
        
        # Running processes
        self.print_info("Running processes (top 20):")
        stdout, stderr, rc = self.run_command("ps aux | head -20")
        if stdout:
            for line in stdout.split('\n'):
                self.print_info(f"  {line}")
        
        # Services running as root
        self.print_info("\nServices running as root:")
        stdout, stderr, rc = self.run_command("ps aux | grep root | grep -v grep | head -10")
        if stdout:
            for line in stdout.split('\n'):
                self.print_info(f"  {line}")
        
        # Network connections
        self.print_info("\nNetwork connections:")
        stdout, stderr, rc = self.run_command("netstat -tulpn 2>/dev/null | head -10")
        if stdout:
            for line in stdout.split('\n'):
                self.print_info(f"  {line}")

    def network_info(self):
        """Gather network information"""
        self.print_section("NETWORK INFORMATION")
        
        # Network interfaces
        stdout, stderr, rc = self.run_command("ip addr show")
        if rc == 0:
            self.print_info("Network interfaces:")
            for line in stdout.split('\n'):
                if line.strip():
                    self.print_info(f"  {line}")
        
        # Listening ports
        self.print_info("\nListening ports:")
        stdout, stderr, rc = self.run_command("ss -tulpn")
        if rc == 0:
            for line in stdout.split('\n'):
                if line.strip():
                    self.print_info(f"  {line}")

    def cron_jobs(self):
        """Check for cron jobs"""
        self.print_section("CRON JOBS")
        
        # System cron jobs
        self.print_info("System cron jobs:")
        stdout, stderr, rc = self.run_command("ls -la /etc/cron* 2>/dev/null")
        if stdout:
            for line in stdout.split('\n'):
                self.print_info(f"  {line}")
        
        # User cron jobs
        self.print_info("\nUser cron jobs:")
        stdout, stderr, rc = self.run_command("crontab -l 2>/dev/null")
        if rc == 0 and stdout:
            for line in stdout.split('\n'):
                self.print_info(f"  {line}")
        else:
            self.print_info("  No user cron jobs found")

    def capabilities(self):
        """Check for Linux capabilities"""
        self.print_section("LINUX CAPABILITIES")
        
        # Files with capabilities
        stdout, stderr, rc = self.run_command("getcap -r / 2>/dev/null | head -20")
        if rc == 0 and stdout:
            self.print_warning("Files with capabilities found:")
            for line in stdout.split('\n'):
                if line.strip():
                    self.print_info(f"  {line}")
        else:
            self.print_info("No files with capabilities found")

    def sudo_info(self):
        """Check sudo configuration"""
        self.print_section("SUDO CONFIGURATION")
        
        # Sudo version
        stdout, stderr, rc = self.run_command("sudo -V 2>/dev/null")
        if rc == 0:
            self.print_info(f"Sudo version: {stdout.split()[2] if len(stdout.split()) > 2 else stdout}")
        
        # Sudo rules for current user
        stdout, stderr, rc = self.run_command("sudo -l 2>/dev/null")
        if rc == 0 and stdout:
            self.print_warning("Sudo rules for current user:")
            for line in stdout.split('\n'):
                self.print_info(f"  {line}")
        else:
            self.print_info("No sudo privileges found")

    def environment_vars(self):
        """Check environment variables"""
        self.print_section("ENVIRONMENT VARIABLES")
        
        # Interesting environment variables
        interesting_vars = ['PATH', 'LD_PRELOAD', 'LD_LIBRARY_PATH', 'SUDO_EDITOR', 'EDITOR']
        for var in interesting_vars:
            value = os.getenv(var)
            if value:
                self.print_info(f"{var}: {value}")

    def interesting_files(self):
        """Look for interesting files"""
        self.print_section("INTERESTING FILES")
        
        # SSH keys
        self.print_info("SSH keys:")
        stdout, stderr, rc = self.run_command("find /home -name 'id_*' -type f 2>/dev/null")
        if stdout:
            for line in stdout.split('\n'):
                if line.strip():
                    self.print_info(f"  {line}")
        
        # Configuration files
        self.print_info("\nInteresting configuration files:")
        config_files = ['/etc/passwd', '/etc/shadow', '/etc/group', '/etc/sudoers']
        for file in config_files:
            if os.path.exists(file):
                stdout, stderr, rc = self.run_command(f"ls -la {file}")
                if rc == 0:
                    self.print_info(f"  {stdout}")

    def run_all_checks(self):
        """Run all privilege escalation checks"""
        self.print_banner()
        
        try:
            self.system_info()
            self.file_permissions()
            self.processes_services()
            self.network_info()
            self.cron_jobs()
            self.capabilities()
            self.sudo_info()
            self.environment_vars()
            self.interesting_files()
            
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
        print("LinPEAS - Linux Privilege Escalation Awesome Script")
        print("Usage: python3 linpeas.py")
        print("No arguments required - just run the script")
        sys.exit(0)
    
    linpeas = LinPEAS()
    linpeas.run_all_checks()

if __name__ == "__main__":
    main()
