"""
Master Script: Complete Data Generation Pipeline
Orchestrates Chutney network setup and traffic generation
"""

import sys
import time
from pathlib import Path
from datetime import datetime
import colorama
from colorama import Fore, Style

# Add scripts to path
sys.path.append(str(Path(__file__).parent))

from chutney_setup import ChutneyNetworkSetup
from traffic_generator import TorTrafficGenerator

colorama.init()


class DataGenerationPipeline:
    """Complete pipeline for Tor data generation"""
    
    def __init__(self, num_requests=100, network_type="basic"):
        """
        Initialize pipeline
        
        Args:
            num_requests: Number of traffic instances to generate
            network_type: Type of Chutney network (basic, medium, large)
        """
        self.num_requests = num_requests
        self.network_type = network_type
        self.network_setup = None
        self.traffic_gen = None
        
    def print_header(self, title):
        """Print formatted header"""
        print(f"\n{Fore.CYAN}{'='*70}")
        print(f"{title:^70}")
        print(f"{'='*70}{Style.RESET_ALL}\n")
        
    def setup_network(self):
        """Setup Chutney Tor network"""
        self.print_header("STEP 1: SETTING UP TOR NETWORK")
        
        self.network_setup = ChutneyNetworkSetup(network_type=self.network_type)
        
        # Create network configuration
        config_path = self.network_setup.create_network_config()
        print(f"✓ Configuration: {config_path}")
        
        # Start network
        print(f"\n{Fore.YELLOW}⏳ Starting Tor network...{Style.RESET_ALL}")
        print("   This may take 30-60 seconds...")
        
        if self.network_setup.start_network():
            print(f"{Fore.GREEN}✓ Tor network is running!{Style.RESET_ALL}")
            return True
        else:
            print(f"{Fore.RED}❌ Failed to start Tor network{Style.RESET_ALL}")
            return False
            
    def generate_traffic(self):
        """Generate traffic through Tor network"""
        self.print_header("STEP 2: GENERATING TRAFFIC & COLLECTING DATA")
        
        # Initialize traffic generator
        # Note: For Chutney, control ports start at 8000, 8001, etc.
        # First client is typically on port 9051
        self.traffic_gen = TorTrafficGenerator(
            control_port=8000,  # Adjust based on your Chutney setup
            socks_port=9000,    # Adjust based on your Chutney setup
            num_requests=self.num_requests
        )
        
        # Connect to Tor controller
        print(f"{Fore.YELLOW}⏳ Connecting to Tor controller...{Style.RESET_ALL}")
        
        if not self.traffic_gen.connect_controller():
            print(f"\n{Fore.YELLOW}⚠️  Connection failed. Trying alternative ports...{Style.RESET_ALL}")
            
            # Try common Chutney control ports
            for port in [8000, 8001, 8002, 9051]:
                print(f"   Trying port {port}...")
                self.traffic_gen.control_port = port
                
                if self.traffic_gen.connect_controller():
                    print(f"{Fore.GREEN}✓ Connected on port {port}!{Style.RESET_ALL}")
                    break
            else:
                print(f"\n{Fore.RED}❌ Could not connect to Tor controller{Style.RESET_ALL}")
                print("\nTroubleshooting:")
                print("1. Check if Chutney network is running:")
                print("   cd <chutney_dir> && ./chutney status networks/basic")
                print("2. Check control ports in Chutney network configuration")
                print("3. Ensure ControlPort is enabled in torrc files")
                return False
                
        # Generate traffic and collect data
        print(f"\n{Fore.CYAN}Starting traffic generation...{Style.RESET_ALL}")
        circuit_data = self.traffic_gen.generate_traffic_sync()
        
        if circuit_data:
            print(f"\n{Fore.GREEN}✓ Traffic generation complete!{Style.RESET_ALL}")
            return True
        else:
            print(f"\n{Fore.RED}❌ No data collected{Style.RESET_ALL}")
            return False
            
    def save_data(self):
        """Save collected data"""
        self.print_header("STEP 3: SAVING DATA")
        
        # Generate timestamped filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"data/circuit_data_{timestamp}.csv"
        
        self.traffic_gen.save_circuit_data(output_file)
        
        print(f"\n{Fore.GREEN}✓ Data saved successfully!{Style.RESET_ALL}")
        print(f"  Location: {output_file}")
        
        return output_file
        
    def cleanup(self):
        """Cleanup resources"""
        self.print_header("STEP 4: CLEANUP")
        
        if self.traffic_gen:
            self.traffic_gen.close()
            
        # Option to stop network
        print(f"\n{Fore.YELLOW}Do you want to stop the Tor network? (y/n):{Style.RESET_ALL} ", end='')
        
        try:
            choice = input().strip().lower()
            if choice == 'y':
                if self.network_setup:
                    self.network_setup.stop_network()
                print(f"{Fore.GREEN}✓ Network stopped{Style.RESET_ALL}")
            else:
                print(f"{Fore.CYAN}ℹ  Network still running (for additional data collection){Style.RESET_ALL}")
        except:
            print(f"\n{Fore.CYAN}ℹ  Network still running{Style.RESET_ALL}")
            
    def run(self):
        """Run complete pipeline"""
        print(f"\n{Fore.CYAN}{'='*70}")
        print(f"{'TOR GUARD PREDICTION - DATA GENERATION PIPELINE':^70}")
        print(f"{'='*70}{Style.RESET_ALL}")
        
        print(f"\nConfiguration:")
        print(f"  Traffic Instances: {self.num_requests}")
        print(f"  Network Type:      {self.network_type}")
        print(f"  Timestamp:         {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            # Step 1: Setup network
            if not self.setup_network():
                print(f"\n{Fore.RED}❌ Pipeline failed at network setup{Style.RESET_ALL}")
                return False
                
            # Step 2: Generate traffic
            if not self.generate_traffic():
                print(f"\n{Fore.RED}❌ Pipeline failed at traffic generation{Style.RESET_ALL}")
                return False
                
            # Step 3: Save data
            output_file = self.save_data()
            
            # Success
            self.print_header("✓ PIPELINE COMPLETE!")
            
            print(f"{Fore.GREEN}Successfully generated and saved circuit data!{Style.RESET_ALL}")
            print(f"\nOutput file: {output_file}")
            print(f"\nNext steps:")
            print(f"  1. Review the data in {output_file}")
            print(f"  2. Run feature extraction")
            print(f"  3. Train ML models")
            
            return True
            
        except KeyboardInterrupt:
            print(f"\n\n{Fore.YELLOW}⚠️  Pipeline interrupted by user{Style.RESET_ALL}")
            return False
            
        except Exception as e:
            print(f"\n{Fore.RED}❌ Pipeline error: {e}{Style.RESET_ALL}")
            import traceback
            traceback.print_exc()
            return False
            
        finally:
            # Cleanup
            self.cleanup()


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Generate Tor circuit data for Guard prediction ML model'
    )
    
    parser.add_argument(
        '-n', '--num-requests',
        type=int,
        default=100,
        help='Number of traffic instances to generate (default: 100)'
    )
    
    parser.add_argument(
        '-t', '--network-type',
        choices=['basic', 'medium', 'large'],
        default='basic',
        help='Chutney network type (default: basic)'
    )
    
    args = parser.parse_args()
    
    # Create and run pipeline
    pipeline = DataGenerationPipeline(
        num_requests=args.num_requests,
        network_type=args.network_type
    )
    
    success = pipeline.run()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
