"""
Simulated TOR Traffic Generator (Windows Compatible)
Generates realistic circuit data WITHOUT requiring Tor/Chutney installation
Perfect for ML training data generation
"""

import random
import string
import csv
from datetime import datetime, timedelta
from pathlib import Path
from tqdm import tqdm
import colorama
from colorama import Fore, Style

colorama.init()


class SimulatedTorNetwork:
    """Simulate a Tor network for data generation"""
    
    def __init__(self, num_guards=5, num_middles=8, num_exits=5):
        """
        Initialize simulated network
        
        Args:
            num_guards: Number of Guard relays
            num_middles: Number of Middle relays
            num_exits: Number of Exit relays
        """
        self.guards = self._generate_relays('Guard', num_guards)
        self.middles = self._generate_relays('Middle', num_middles)
        self.exits = self._generate_relays('Exit', num_exits)
        
    def _generate_fingerprint(self):
        """Generate realistic relay fingerprint (40 hex chars)"""
        return ''.join(random.choices('0123456789ABCDEF', k=40))
        
    def _generate_ip_address(self):
        """Generate realistic IP address"""
        return f"127.0.{random.randint(0, 255)}.{random.randint(1, 254)}"
        
    def _generate_relays(self, relay_type, count):
        """Generate relay nodes"""
        relays = []
        countries = ['US', 'DE', 'FR', 'GB', 'NL', 'SE', 'JP', 'CA', 'CH', 'AT']
        
        for i in range(count):
            relay = {
                'fingerprint': self._generate_fingerprint(),
                'nickname': f"{relay_type}Node{i+1}",
                'address': self._generate_ip_address(),
                'country': random.choice(countries),
                'bandwidth': random.randint(1000000, 10000000),  # 1-10 MB/s
                'uptime': random.randint(1000000, 10000000),  # seconds
            }
            relays.append(relay)
            
        return relays
        
    def select_circuit_path(self, used_paths=None):
        """
        Select random Guard->Middle->Exit path
        
        Args:
            used_paths: Set of already used (guard_fp, middle_fp, exit_fp) tuples
        """
        max_attempts = 100
        attempts = 0
        
        while attempts < max_attempts:
            guard = random.choice(self.guards)
            middle = random.choice(self.middles)
            exit_relay = random.choice(self.exits)
            
            # If we're tracking uniqueness, check if this path was used
            if used_paths is not None:
                path_key = (guard['fingerprint'], middle['fingerprint'], exit_relay['fingerprint'])
                if path_key not in used_paths:
                    used_paths.add(path_key)
                    return guard, middle, exit_relay
            else:
                return guard, middle, exit_relay
            
            attempts += 1
        
        # If we can't find unique path after max attempts, return anyway
        return guard, middle, exit_relay


class SimulatedTrafficGenerator:
    """Generate simulated traffic data for ML training"""
    
    def __init__(self, num_requests=100, num_guards=5, num_middles=8, num_exits=5):
        """
        Initialize generator
        
        Args:
            num_requests: Number of traffic instances to generate
            num_guards: Number of Guard relays (default: 5)
            num_middles: Number of Middle relays (default: 8)
            num_exits: Number of Exit relays (default: 5)
        """
        self.num_requests = num_requests
        self.network = SimulatedTorNetwork(
            num_guards=num_guards,
            num_middles=num_middles,
            num_exits=num_exits
        )
        self.circuit_data = []
        
    def generate_traffic(self):
        """Generate simulated traffic and collect circuit data"""
        
        print(f"\n{Fore.CYAN}{'='*70}")
        print(f"{'GENERATING SIMULATED TOR TRAFFIC':^70}")
        print(f"{'='*70}{Style.RESET_ALL}\n")
        
        print(f"Network Configuration:")
        print(f"  Guards:  {len(self.network.guards)}")
        print(f"  Middles: {len(self.network.middles)}")
        print(f"  Exits:   {len(self.network.exits)}")
        print(f"\nGenerating {self.num_requests} traffic instances...\n")
        
        base_time = datetime.now()
        circuit_data = []
        used_paths = set()  # Track used paths for uniqueness
        
        with tqdm(total=self.num_requests, 
                  desc="Generating circuits",
                  bar_format="{l_bar}%s{bar}%s{r_bar}" % (Fore.GREEN, Style.RESET_ALL)) as pbar:
            
            for i in range(self.num_requests):
                # Select random circuit path (ensuring uniqueness)
                guard, middle, exit_relay = self.network.select_circuit_path(used_paths)
                
                # Generate circuit metadata
                circuit_id = 1000 + i
                timestamp = base_time + timedelta(seconds=i * random.uniform(0.5, 2.0))
                build_time = timestamp - timedelta(milliseconds=random.randint(100, 1000))
                
                circuit_info = {
                    'request_id': i + 1,
                    'circuit_id': circuit_id,
                    'timestamp': timestamp.isoformat(),
                    'status': 'BUILT',
                    
                    # Guard information
                    'guard_fingerprint': guard['fingerprint'],
                    'guard_nickname': guard['nickname'],
                    'guard_address': guard['address'],
                    'guard_country': guard['country'],
                    
                    # Middle information
                    'middle_fingerprint': middle['fingerprint'],
                    'middle_nickname': middle['nickname'],
                    'middle_address': middle['address'],
                    'middle_country': middle['country'],
                    
                    # Exit information
                    'exit_fingerprint': exit_relay['fingerprint'],
                    'exit_nickname': exit_relay['nickname'],
                    'exit_address': exit_relay['address'],
                    'exit_country': exit_relay['country'],
                    
                    # Circuit metadata
                    'build_time': build_time.isoformat(),
                    'purpose': 'GENERAL',
                    
                    # Additional features for ML
                    'guard_bandwidth': guard['bandwidth'],
                    'middle_bandwidth': middle['bandwidth'],
                    'exit_bandwidth': exit_relay['bandwidth'],
                    'circuit_setup_duration': random.uniform(0.5, 2.5),
                    'total_bytes': random.randint(10000, 1000000),
                }
                
                circuit_data.append(circuit_info)
                pbar.update(1)
                
        self.circuit_data = circuit_data
        
        print(f"\n{Fore.GREEN}✓ Successfully generated {len(circuit_data)} circuits{Style.RESET_ALL}")
        
        return circuit_data
        
    def save_data(self, output_file='data/circuit_data.csv'):
        """Save circuit data to CSV"""
        
        if not self.circuit_data:
            print(f"{Fore.RED}❌ No data to save{Style.RESET_ALL}")
            return
            
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Generate timestamped filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = output_path.parent / f"circuit_data_{timestamp}.csv"
        
        # Define CSV columns
        fieldnames = [
            'request_id', 'circuit_id', 'timestamp', 'status',
            'guard_fingerprint', 'guard_nickname', 'guard_address', 'guard_country',
            'middle_fingerprint', 'middle_nickname', 'middle_address', 'middle_country',
            'exit_fingerprint', 'exit_nickname', 'exit_address', 'exit_country',
            'build_time', 'purpose',
            'guard_bandwidth', 'middle_bandwidth', 'exit_bandwidth',
            'circuit_setup_duration', 'total_bytes'
        ]
        
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.circuit_data)
            
        print(f"\n{Fore.GREEN}{'='*70}")
        print(f"✓ DATA SAVED SUCCESSFULLY")
        print(f"{'='*70}{Style.RESET_ALL}\n")
        
        print(f"Output file: {Fore.CYAN}{output_file}{Style.RESET_ALL}")
        print(f"Total records: {len(self.circuit_data)}")
        
        # Print statistics
        self._print_statistics()
        
        return output_file
        
    def _print_statistics(self):
        """Print data statistics"""
        
        if not self.circuit_data:
            return
            
        print(f"\n{Fore.CYAN}{'='*70}")
        print(f"DATA STATISTICS")
        print(f"{'='*70}{Style.RESET_ALL}\n")
        
        # Count unique relays
        unique_guards = set(c['guard_fingerprint'] for c in self.circuit_data)
        unique_middles = set(c['middle_fingerprint'] for c in self.circuit_data)
        unique_exits = set(c['exit_fingerprint'] for c in self.circuit_data)
        
        print(f"Total Circuits:     {len(self.circuit_data)}")
        print(f"Unique Guards:      {len(unique_guards)}")
        print(f"Unique Middles:     {len(unique_middles)}")
        print(f"Unique Exits:       {len(unique_exits)}")
        
        # Count Guard-Exit pairs
        guard_exit_pairs = {}
        for c in self.circuit_data:
            pair = (c['guard_nickname'], c['exit_nickname'])
            guard_exit_pairs[pair] = guard_exit_pairs.get(pair, 0) + 1
            
        print(f"\n{Fore.YELLOW}Top 5 Guard-Exit Pairs:{Style.RESET_ALL}")
        for i, (pair, count) in enumerate(sorted(guard_exit_pairs.items(), 
                                                   key=lambda x: x[1], 
                                                   reverse=True)[:5], 1):
            print(f"  {i}. {pair[0]} → {pair[1]}: {count} times")
            
        # Country distribution
        exit_countries = {}
        for c in self.circuit_data:
            country = c['exit_country']
            exit_countries[country] = exit_countries.get(country, 0) + 1
            
        print(f"\n{Fore.YELLOW}Exit Country Distribution:{Style.RESET_ALL}")
        for country, count in sorted(exit_countries.items(), 
                                      key=lambda x: x[1], 
                                      reverse=True)[:5]:
            print(f"  {country}: {count} circuits ({count/len(self.circuit_data)*100:.1f}%)")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Generate simulated Tor circuit data (Windows compatible)'
    )
    
    parser.add_argument(
        '-n', '--num-requests',
        type=int,
        default=100,
        help='Number of traffic instances to generate (default: 100)'
    )
    
    parser.add_argument(
        '-g', '--guards',
        type=int,
        default=5,
        help='Number of Guard relays (default: 5)'
    )
    
    parser.add_argument(
        '-m', '--middles',
        type=int,
        default=8,
        help='Number of Middle relays (default: 8)'
    )
    
    parser.add_argument(
        '-e', '--exits',
        type=int,
        default=5,
        help='Number of Exit relays (default: 5)'
    )
    
    args = parser.parse_args()
    
    print(f"\n{Fore.CYAN}{'='*70}")
    print(f"{'TOR GUARD PREDICTION - SIMULATED DATA GENERATOR':^70}")
    print(f"{'='*70}{Style.RESET_ALL}\n")
    
    print(f"Configuration:")
    print(f"  Traffic Instances: {args.num_requests}")
    print(f"  Guards:            {args.guards}")
    print(f"  Middles:           {args.middles}")
    print(f"  Exits:             {args.exits}")
    print(f"  Timestamp:         {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Mode:              Simulated (Windows Compatible)")
    
    try:
        # Create generator
        generator = SimulatedTrafficGenerator(
            num_requests=args.num_requests,
            num_guards=args.guards,
            num_middles=args.middles,
            num_exits=args.exits
        )
        
        # Generate traffic
        generator.generate_traffic()
        
        # Save data
        output_file = generator.save_data()
        
        print(f"\n{Fore.GREEN}{'='*70}")
        print(f"✓ GENERATION COMPLETE!")
        print(f"{'='*70}{Style.RESET_ALL}\n")
        
        print(f"Next steps:")
        print(f"  1. Review data: {output_file}")
        print(f"  2. Run feature extraction")
        print(f"  3. Train ML models (XGBoost/LightGBM)")
        print(f"  4. Evaluate with Top-K accuracy and MRR")
        
        print(f"\n{Fore.YELLOW}Note: This is simulated data for ML training.{Style.RESET_ALL}")
        print(f"For production, use real Tor/Chutney setup.")
        
    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}⚠️  Interrupted by user{Style.RESET_ALL}")
        
    except Exception as e:
        print(f"\n{Fore.RED}❌ Error: {e}{Style.RESET_ALL}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
