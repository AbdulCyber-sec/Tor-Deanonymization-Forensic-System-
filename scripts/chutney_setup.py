"""
Chutney Network Setup and Configuration
Creates a Tor network with Guards, Middles, and Exits
"""

import os
import subprocess
import time
import yaml
from pathlib import Path


class ChutneyNetworkSetup:
    """Setup and manage Chutney Tor network"""
    
    def __init__(self, chutney_path=None, network_type="basic"):
        """
        Initialize Chutney setup
        
        Args:
            chutney_path: Path to Chutney installation
            network_type: Network configuration (basic, medium, large)
        """
        self.chutney_path = chutney_path or self._find_chutney()
        self.network_type = network_type
        self.network_dir = Path("tor_simulation/chutney_network")
        self.network_dir.mkdir(parents=True, exist_ok=True)
        
    def _find_chutney(self):
        """Try to find Chutney installation"""
        possible_paths = [
            Path.home() / "chutney",
            Path("/opt/chutney"),
            Path("C:/tor/chutney"),
            Path("./chutney")
        ]
        
        for path in possible_paths:
            if path.exists() and (path / "chutney").exists():
                return path
                
        print("⚠️  Chutney not found. Please install from:")
        print("   git clone https://git.torproject.org/chutney.git")
        return None
        
    def create_network_config(self):
        """
        Create custom network configuration
        Returns path to network config file
        """
        
        # Define network topology
        if self.network_type == "basic":
            config = self._create_basic_network()
        elif self.network_type == "medium":
            config = self._create_medium_network()
        else:
            config = self._create_large_network()
            
        config_path = self.network_dir / f"network_{self.network_type}.yaml"
        
        with open(config_path, 'w') as f:
            yaml.dump(config, f)
            
        print(f"✓ Network configuration created: {config_path}")
        return config_path
        
    def _create_basic_network(self):
        """Basic network: 3 Guards, 3 Middles, 3 Exits"""
        return {
            'guards': 3,
            'middles': 3,
            'exits': 3,
            'clients': 5,
            'authorities': 1
        }
        
    def _create_medium_network(self):
        """Medium network: 5 Guards, 8 Middles, 5 Exits"""
        return {
            'guards': 5,
            'middles': 8,
            'exits': 5,
            'clients': 10,
            'authorities': 1
        }
        
    def _create_large_network(self):
        """Large network: 10 Guards, 15 Middles, 10 Exits"""
        return {
            'guards': 10,
            'middles': 15,
            'exits': 10,
            'clients': 20,
            'authorities': 1
        }
        
    def start_network(self):
        """Start the Chutney Tor network"""
        
        if not self.chutney_path:
            print("❌ Cannot start network: Chutney not found")
            return False
            
        print(f"\n{'='*60}")
        print("STARTING TOR NETWORK WITH CHUTNEY")
        print(f"{'='*60}\n")
        
        try:
            # Use Chutney's built-in network configurations
            network_name = "networks/basic" if self.network_type == "basic" else "networks/basic"
            
            os.chdir(self.chutney_path)
            
            # Configure network
            print("⏳ Configuring network...")
            subprocess.run([
                "./chutney", "configure", network_name
            ], check=True)
            
            # Start network
            print("⏳ Starting Tor network...")
            subprocess.run([
                "./chutney", "start", network_name
            ], check=True)
            
            # Wait for network to stabilize
            print("⏳ Waiting for network to stabilize (30 seconds)...")
            time.sleep(30)
            
            # Verify network
            result = subprocess.run([
                "./chutney", "status", network_name
            ], capture_output=True, text=True)
            
            if "nodes are running" in result.stdout:
                print("\n✓ Tor network is RUNNING")
                return True
            else:
                print("\n⚠️  Network status unclear")
                print(result.stdout)
                return False
                
        except subprocess.CalledProcessError as e:
            print(f"\n❌ Error starting network: {e}")
            return False
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            return False
            
    def stop_network(self):
        """Stop the Chutney network"""
        if not self.chutney_path:
            return
            
        try:
            os.chdir(self.chutney_path)
            network_name = "networks/basic"
            
            print("\n⏳ Stopping Tor network...")
            subprocess.run([
                "./chutney", "stop", network_name
            ], check=True)
            
            print("✓ Network stopped")
            
        except Exception as e:
            print(f"⚠️  Error stopping network: {e}")
            
    def get_network_info(self):
        """Get information about running network"""
        
        if not self.chutney_path:
            return None
            
        try:
            os.chdir(self.chutney_path)
            network_name = "networks/basic"
            
            result = subprocess.run([
                "./chutney", "status", network_name
            ], capture_output=True, text=True, check=True)
            
            return result.stdout
            
        except Exception as e:
            print(f"⚠️  Error getting network info: {e}")
            return None


if __name__ == "__main__":
    # Test setup
    setup = ChutneyNetworkSetup(network_type="basic")
    
    # Create config
    setup.create_network_config()
    
    # Start network
    if setup.start_network():
        print("\n✓ Network setup complete!")
        print("\nPress Ctrl+C to stop...")
        
        try:
            while True:
                time.sleep(10)
        except KeyboardInterrupt:
            setup.stop_network()
