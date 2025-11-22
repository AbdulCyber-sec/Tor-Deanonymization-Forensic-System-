"""
Traffic Generator for Tor Network
Generates 100+ concurrent traffic instances and collects circuit data
"""

import asyncio
import aiohttp
import socks
import socket
from stem import CircuitStatus
from stem.control import Controller
import time
import random
from datetime import datetime
from pathlib import Path
import csv
from tqdm import tqdm
import colorama
from colorama import Fore, Style

colorama.init()


class TorTrafficGenerator:
    """Generate traffic through Tor network and collect circuit data"""
    
    def __init__(self, control_port=9051, socks_port=9050, num_requests=100):
        """
        Initialize traffic generator
        
        Args:
            control_port: Tor control port
            socks_port: Tor SOCKS proxy port
            num_requests: Number of concurrent traffic instances
        """
        self.control_port = control_port
        self.socks_port = socks_port
        self.num_requests = num_requests
        self.circuit_data = []
        self.controller = None
        
    def connect_controller(self):
        """Connect to Tor controller"""
        try:
            self.controller = Controller.from_port(port=self.control_port)
            self.controller.authenticate()
            print(f"✓ Connected to Tor controller on port {self.control_port}")
            return True
        except Exception as e:
            print(f"❌ Failed to connect to Tor controller: {e}")
            print(f"   Make sure Tor is running on control port {self.control_port}")
            return False
            
    def get_circuit_info(self, circuit_id):
        """
        Get detailed information about a circuit
        
        Returns:
            Dictionary with Guard, Middle, Exit information
        """
        try:
            circuit = self.controller.get_circuit(circuit_id)
            
            if not circuit.path or len(circuit.path) < 3:
                return None
                
            # Extract path: Guard -> Middle -> Exit
            guard_fp = circuit.path[0][0]
            middle_fp = circuit.path[1][0]
            exit_fp = circuit.path[2][0]
            
            # Get relay descriptors
            guard_desc = self.controller.get_network_status(guard_fp)
            middle_desc = self.controller.get_network_status(middle_fp)
            exit_desc = self.controller.get_network_status(exit_fp)
            
            circuit_info = {
                'circuit_id': circuit_id,
                'timestamp': datetime.now().isoformat(),
                'status': circuit.status.name,
                
                # Guard info
                'guard_fingerprint': guard_fp,
                'guard_nickname': guard_desc.nickname if guard_desc else 'Unknown',
                'guard_address': guard_desc.address if guard_desc else 'Unknown',
                'guard_country': self._get_country(guard_fp),
                
                # Middle info
                'middle_fingerprint': middle_fp,
                'middle_nickname': middle_desc.nickname if middle_desc else 'Unknown',
                'middle_address': middle_desc.address if middle_desc else 'Unknown',
                'middle_country': self._get_country(middle_fp),
                
                # Exit info
                'exit_fingerprint': exit_fp,
                'exit_nickname': exit_desc.nickname if exit_desc else 'Unknown',
                'exit_address': exit_desc.address if exit_desc else 'Unknown',
                'exit_country': self._get_country(exit_fp),
                
                # Circuit metadata
                'build_time': circuit.created.isoformat() if circuit.created else None,
                'purpose': circuit.purpose if hasattr(circuit, 'purpose') else 'GENERAL',
            }
            
            return circuit_info
            
        except Exception as e:
            print(f"⚠️  Error getting circuit info: {e}")
            return None
            
    def _get_country(self, fingerprint):
        """Get country for relay (simulated for Chutney)"""
        # For Chutney local network, all nodes are 'local'
        # In real implementation, use GeoIP lookup
        countries = ['US', 'DE', 'FR', 'GB', 'NL', 'SE', 'JP', 'CA']
        # Hash fingerprint to consistently assign country
        return countries[hash(fingerprint) % len(countries)]
        
    async def make_tor_request(self, session, request_id):
        """
        Make a single request through Tor
        
        Args:
            session: aiohttp session
            request_id: Request identifier
            
        Returns:
            Circuit information
        """
        try:
            # Configure SOCKS proxy
            proxy = f"socks5://127.0.0.1:{self.socks_port}"
            
            # Test URLs (can be changed to your needs)
            test_urls = [
                'http://example.com',
                'http://httpbin.org/get',
                'http://www.google.com',
                'http://www.wikipedia.org'
            ]
            
            url = random.choice(test_urls)
            
            # Make request through Tor
            async with session.get(url, proxy=proxy, timeout=30) as response:
                status = response.status
                
                # Get the circuit that was used
                # Note: We need to query Tor controller for circuit info
                circuits = self.controller.get_circuits()
                
                # Find most recent built circuit
                active_circuits = [c for c in circuits if c.status == CircuitStatus.BUILT]
                
                if active_circuits:
                    # Use the most recently created circuit
                    circuit = sorted(active_circuits, key=lambda x: x.id)[-1]
                    circuit_info = self.get_circuit_info(circuit.id)
                    
                    if circuit_info:
                        circuit_info['request_id'] = request_id
                        circuit_info['http_status'] = status
                        circuit_info['target_url'] = url
                        return circuit_info
                        
        except asyncio.TimeoutError:
            print(f"{Fore.YELLOW}⏱  Request {request_id} timed out{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}❌ Request {request_id} failed: {e}{Style.RESET_ALL}")
            
        return None
        
    async def generate_traffic_batch(self, batch_size=10):
        """
        Generate a batch of traffic concurrently
        
        Args:
            batch_size: Number of concurrent requests
        """
        connector = aiohttp.TCPConnector(limit=batch_size)
        
        async with aiohttp.ClientSession(connector=connector) as session:
            tasks = []
            
            for i in range(batch_size):
                task = self.make_tor_request(session, i)
                tasks.append(task)
                
                # Small delay between requests
                await asyncio.sleep(0.1)
                
            # Wait for all requests to complete
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filter successful results
            valid_results = [r for r in results if r is not None and not isinstance(r, Exception)]
            
            return valid_results
            
    def generate_traffic_sync(self):
        """
        Generate traffic synchronously (simpler approach for Chutney)
        Creates new circuits and collects their information
        """
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"GENERATING {self.num_requests} TRAFFIC INSTANCES")
        print(f"{'='*60}{Style.RESET_ALL}\n")
        
        circuit_data = []
        
        with tqdm(total=self.num_requests, desc="Generating traffic", 
                  bar_format="{l_bar}%s{bar}%s{r_bar}" % (Fore.GREEN, Style.RESET_ALL)) as pbar:
            
            for i in range(self.num_requests):
                try:
                    # Create a new circuit
                    circuit_id = self.controller.new_circuit(await_build=True)
                    
                    # Wait a moment for circuit to stabilize
                    time.sleep(0.5)
                    
                    # Get circuit information
                    circuit_info = self.get_circuit_info(circuit_id)
                    
                    if circuit_info:
                        circuit_info['request_id'] = i + 1
                        circuit_data.append(circuit_info)
                        pbar.update(1)
                        
                        # Print progress every 10 requests
                        if (i + 1) % 10 == 0:
                            print(f"\n{Fore.GREEN}✓ Generated {i+1}/{self.num_requests} circuits{Style.RESET_ALL}")
                    else:
                        pbar.update(1)
                        
                    # Small delay to avoid overwhelming the network
                    time.sleep(0.2)
                    
                except Exception as e:
                    print(f"\n{Fore.RED}❌ Error creating circuit {i+1}: {e}{Style.RESET_ALL}")
                    pbar.update(1)
                    continue
                    
        self.circuit_data = circuit_data
        
        print(f"\n{Fore.GREEN}✓ Successfully generated {len(circuit_data)} circuits{Style.RESET_ALL}")
        return circuit_data
        
    def save_circuit_data(self, output_file='data/circuit_data.csv'):
        """
        Save collected circuit data to CSV
        
        Args:
            output_file: Path to output CSV file
        """
        if not self.circuit_data:
            print("⚠️  No circuit data to save")
            return
            
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Define CSV columns
        fieldnames = [
            'request_id', 'circuit_id', 'timestamp', 'status',
            'guard_fingerprint', 'guard_nickname', 'guard_address', 'guard_country',
            'middle_fingerprint', 'middle_nickname', 'middle_address', 'middle_country',
            'exit_fingerprint', 'exit_nickname', 'exit_address', 'exit_country',
            'build_time', 'purpose'
        ]
        
        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for circuit in self.circuit_data:
                # Only write fields that exist in fieldnames
                row = {k: circuit.get(k, '') for k in fieldnames}
                writer.writerow(row)
                
        print(f"\n{Fore.GREEN}✓ Circuit data saved to: {output_path}{Style.RESET_ALL}")
        print(f"  Total circuits: {len(self.circuit_data)}")
        
        # Print summary statistics
        self._print_summary()
        
    def _print_summary(self):
        """Print summary statistics of collected data"""
        if not self.circuit_data:
            return
            
        print(f"\n{Fore.CYAN}{'='*60}")
        print("DATA SUMMARY")
        print(f"{'='*60}{Style.RESET_ALL}\n")
        
        # Count unique relays
        unique_guards = set(c['guard_fingerprint'] for c in self.circuit_data)
        unique_middles = set(c['middle_fingerprint'] for c in self.circuit_data)
        unique_exits = set(c['exit_fingerprint'] for c in self.circuit_data)
        
        print(f"Total Circuits:     {len(self.circuit_data)}")
        print(f"Unique Guards:      {len(unique_guards)}")
        print(f"Unique Middles:     {len(unique_middles)}")
        print(f"Unique Exits:       {len(unique_exits)}")
        
        # Most common Guard-Exit pairs
        guard_exit_pairs = {}
        for c in self.circuit_data:
            pair = (c['guard_nickname'], c['exit_nickname'])
            guard_exit_pairs[pair] = guard_exit_pairs.get(pair, 0) + 1
            
        print(f"\nTop 5 Guard-Exit Pairs:")
        for i, (pair, count) in enumerate(sorted(guard_exit_pairs.items(), 
                                                   key=lambda x: x[1], 
                                                   reverse=True)[:5], 1):
            print(f"  {i}. {pair[0]} → {pair[1]}: {count} times")
            
    def close(self):
        """Close controller connection"""
        if self.controller:
            self.controller.close()
            print("\n✓ Controller connection closed")


if __name__ == "__main__":
    # Example usage
    generator = TorTrafficGenerator(num_requests=100)
    
    if generator.connect_controller():
        # Generate traffic
        circuit_data = generator.generate_traffic_sync()
        
        # Save data
        generator.save_circuit_data('data/circuit_data.csv')
        
        # Close connection
        generator.close()
    else:
        print("\n❌ Failed to connect to Tor. Please ensure:")
        print("   1. Tor/Chutney network is running")
        print("   2. Control port is accessible")
        print("   3. Authentication is configured")
