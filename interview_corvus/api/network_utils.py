"""
Network utilities for web server setup.
Handles IP address discovery and port availability checking.
"""

import socket
import subprocess
import platform
from typing import List, Tuple, Optional
from loguru import logger


def get_local_ip_addresses() -> List[str]:
    """
    Get all local IP addresses including LAN addresses.
    
    Returns:
        List of IP addresses (including 127.0.0.1, 192.168.x.x, etc.)
    """
    ip_addresses = []
    
    try:
        # Method 1: Connect to external address to get primary local IP
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect(("8.8.8.8", 80))
        sockname = sock.getsockname()
        print(sockname)
        primary_ip = sockname[0]
        sock.close()
        
        if primary_ip and primary_ip not in ip_addresses:
            ip_addresses.append(primary_ip)
            
    except Exception as e:
        logger.debug(f"Could not get primary IP via socket method: {e}")
    
    # Method 2: Use hostname resolution
    try:
        hostname = socket.gethostname()
        host_ip = socket.gethostbyname(hostname)
        if host_ip and host_ip not in ip_addresses:
            ip_addresses.append(host_ip)
    except Exception as e:
        logger.debug(f"Could not get IP via hostname method: {e}")
    
    # Method 3: Platform-specific network interface discovery
    try:
        if platform.system() == "Darwin":  # macOS
            # Use ifconfig to get network interfaces
            result = subprocess.run(
                ["ifconfig"], 
                capture_output=True, 
                text=True, 
                timeout=5
            )
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'inet ' in line and 'netmask' in line:
                        parts = line.strip().split()
                        if len(parts) > 1:
                            ip = parts[1]
                            # Include common LAN ranges and localhost
                            if (ip.startswith('192.168.') or 
                                ip.startswith('10.') or 
                                ip.startswith('172.') or 
                                ip == '127.0.0.1'):
                                if ip not in ip_addresses:
                                    ip_addresses.append(ip)
                                    
        elif platform.system() == "Linux":
            # Use ip addr or ifconfig
            try:
                result = subprocess.run(
                    ["ip", "addr"], 
                    capture_output=True, 
                    text=True, 
                    timeout=5
                )
                if result.returncode == 0:
                    lines = result.stdout.split('\n')
                    for line in lines:
                        if 'inet ' in line and 'scope global' in line:
                            parts = line.strip().split()
                            if len(parts) > 1:
                                ip_with_mask = parts[1]
                                ip = ip_with_mask.split('/')[0]
                                if ip not in ip_addresses:
                                    ip_addresses.append(ip)
            except FileNotFoundError:
                # Fallback to ifconfig if ip command not available
                result = subprocess.run(
                    ["ifconfig"], 
                    capture_output=True, 
                    text=True, 
                    timeout=5
                )
                if result.returncode == 0:
                    lines = result.stdout.split('\n')
                    for line in lines:
                        if 'inet ' in line:
                            parts = line.strip().split()
                            for i, part in enumerate(parts):
                                if part == 'inet' and i + 1 < len(parts):
                                    ip = parts[i + 1]
                                    if (ip.startswith('192.168.') or 
                                        ip.startswith('10.') or 
                                        ip.startswith('172.') or 
                                        ip == '127.0.0.1'):
                                        if ip not in ip_addresses:
                                            ip_addresses.append(ip)
                                            
        elif platform.system() == "Windows":
            # Use ipconfig
            result = subprocess.run(
                ["ipconfig"], 
                capture_output=True, 
                text=True, 
                timeout=5,
                shell=True
            )
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'IPv4 Address' in line or 'IP Address' in line:
                        parts = line.split(':')
                        if len(parts) > 1:
                            ip = parts[1].strip()
                            if (ip.startswith('192.168.') or 
                                ip.startswith('10.') or 
                                ip.startswith('172.') or 
                                ip == '127.0.0.1'):
                                if ip not in ip_addresses:
                                    ip_addresses.append(ip)
                                    
    except Exception as e:
        logger.debug(f"Could not get IPs via system commands: {e}")
    
    # Always ensure localhost is included
    if '127.0.0.1' not in ip_addresses:
        ip_addresses.append('127.0.0.1')
    
    # Sort IP addresses: localhost first, then LAN addresses
    def sort_key(ip):
        if ip == '127.0.0.1':
            return '0'
        elif ip.startswith('192.168.'):
            return '1' + ip
        elif ip.startswith('10.'):
            return '2' + ip
        elif ip.startswith('172.'):
            return '3' + ip
        else:
            return '9' + ip
    
    ip_addresses.sort(key=sort_key)
    
    logger.info(f"Discovered IP addresses: {ip_addresses}")
    return ip_addresses


def is_port_available(host: str, port: int) -> bool:
    """
    Check if a port is available on the given host.
    
    Args:
        host: Host address to check
        port: Port number to check
        
    Returns:
        True if port is available, False otherwise
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(1)
            result = sock.connect_ex((host, port))
            return result != 0
    except Exception as e:
        logger.debug(f"Error checking port {port} on {host}: {e}")
        return False


def find_available_port(host: str, start_port: int = 26262, max_attempts: int = 100) -> Optional[int]:
    """
    Find an available port starting from the given port number.
    
    Args:
        host: Host address to check ports on
        start_port: Starting port number to check
        max_attempts: Maximum number of ports to check
        
    Returns:
        Available port number or None if no port found
    """
    for port in range(start_port, start_port + max_attempts):
        if is_port_available(host, port):
            logger.info(f"Found available port: {port} on {host}")
            return port
    
    logger.error(f"Could not find available port starting from {start_port} on {host}")
    return None


def get_server_addresses(host: str, port: int) -> List[str]:
    """
    Get all possible server addresses for the given host and port.
    
    Args:
        host: Host address (e.g., "0.0.0.0")
        port: Port number
        
    Returns:
        List of server URLs
    """
    addresses = []
    
    if host == "0.0.0.0":
        # Server is bound to all interfaces, get all local IPs
        local_ips = get_local_ip_addresses()
        for ip in local_ips:
            addresses.append(f"http://{ip}:{port}")
    else:
        # Server is bound to specific host
        addresses.append(f"http://{host}:{port}")
    
    return addresses


def print_server_info(host: str, port: int, app_name: str = "AceBot"):
    """
    Print formatted server information with all accessible addresses.
    
    Args:
        host: Server host
        port: Server port
        app_name: Application name for display
    """
    addresses = get_server_addresses(host, port)
    
    print("=" * 60)
    print(f"🌐 {app_name} Integrated Web Server")
    print("=" * 60)
    print("📍 Server accessible at:")
    
    for i, address in enumerate(addresses, 1):
        icon = "🏠" if "127.0.0.1" in address else "🌐"
        name = "Localhost" if "127.0.0.1" in address else "Network"
        print(f"   {icon} {name:12} {address}")
    
    print(f"📚 API Documentation: {addresses[0]}/docs")
    print(f"📖 ReDoc Documentation: {addresses[0]}/redoc")
    print("=" * 60)
