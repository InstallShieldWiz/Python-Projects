#!/usr/bin/env python3
"""
MacPEAS - macOS Privilege Escalation Awesome Script
Python implementation for macOS privilege escalation enumeration
"""

import os
import sys
import subprocess
import json
import re
import plistlib
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

class MacPEAS:
    def __init__(self):
        self.results = {}
        self.start_time = datetime.now()
        
    def print_banner(self):
        """Print MacPEAS banner"""
        banner = f"""
{Colors.CYAN}{Colors.BOLD}
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║                              MACPEAS                                        ║
║                                                                              ║
║                    macOS Privilege Escalation Awesome Script                ║
║                              by ISW                                          ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
{Colors.END}
"""
        print(banner)
        print(f"{Colors.GREEN}[+] Starting MacPEAS at {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}{Colors.END}\n")

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
        self.print_info(f"OS: {platform.system()} {platform.release()}")
        self.print_info(f"Architecture: {platform.architecture()[0]}")
        self.print_info(f"Machine: {platform.machine()}")
        self.print_info(f"Processor: {platform.processor()}")
        
        # macOS specific info
        stdout, stderr, rc = self.run_command("sw_vers")
        if rc == 0:
            self.print_info("macOS Version Information:")
            for line in stdout.split('\n'):
                self.print_info(f"  {line}")
        
        # Current user
        self.print_info(f"Current User: {os.getenv('USER', 'unknown')}")
        self.print_info(f"Home Directory: {os.getenv('HOME', 'unknown')}")
        
        # System uptime
        stdout, stderr, rc = self.run_command("uptime")
        if rc == 0:
            self.print_info(f"System Uptime: {stdout}")

    def run_all_checks(self):
        """Run all privilege escalation checks"""
        self.print_banner()
        
        try:
            self.system_info()
            
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
        print("MacPEAS - macOS Privilege Escalation Awesome Script")
        print("Usage: python3 macpeas.py")
        print("No arguments required - just run the script")
        sys.exit(0)
    
    # Check if running on macOS
    if platform.system() != 'Darwin':
        print("This script is designed for macOS systems only.")
        sys.exit(1)
    
    macpeas = MacPEAS()
    macpeas.run_all_checks()

if __name__ == "__main__":
    main()
