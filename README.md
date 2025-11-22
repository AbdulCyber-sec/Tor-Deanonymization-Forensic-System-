# TOR Guard Prediction - Data Generation System

## 🎯 Overview

This system generates training data for TOR Guard prediction by:
1. Setting up a local Tor network using Chutney
2. Generating 100+ concurrent traffic instances
3. Collecting circuit data (Guard, Middle, Exit info)
4. Saving data with fingerprints, addresses, nicknames, countries, timestamps

## 📋 Prerequisites

### 1. Install Tor
```bash
# Windows (using Chocolatey)
choco install tor

# Or download from: https://www.torproject.org/download/
```

### 2. Install Chutney
```bash
git clone https://git.torproject.org/chutney.git
cd chutney
```

### 3. Install Python Dependencies
```bash
pip install -r requirements.txt
```

## 🚀 Quick Start

### Option 1: Run Complete Pipeline (Recommended)

Generate 100 traffic instances with one command:

```bash
python scripts/generate_data.py
```

With custom parameters:

```bash
# Generate 200 instances
python scripts/generate_data.py -n 200

# Use medium network (more relays)
python scripts/generate_data.py -t medium -n 150
```

### Option 2: Manual Step-by-Step

#### Step 1: Setup Chutney Network

```bash
python scripts/chutney_setup.py
```

#### Step 2: Generate Traffic & Collect Data

```bash
python scripts/traffic_generator.py
```

## 📊 Output Data Format

The system generates a CSV file with the following columns:

```
request_id              - Sequential ID (1, 2, 3, ...)
circuit_id              - Tor circuit ID
timestamp               - ISO format timestamp
status                  - Circuit status (BUILT)

guard_fingerprint       - Guard relay fingerprint
guard_nickname          - Guard relay nickname
guard_address           - Guard IP address
guard_country           - Guard country code

middle_fingerprint      - Middle relay fingerprint
middle_nickname         - Middle relay nickname
middle_address          - Middle IP address
middle_country          - Middle country code

exit_fingerprint        - Exit relay fingerprint
exit_nickname           - Exit relay nickname
exit_address            - Exit IP address
exit_country            - Exit country code

build_time              - Circuit build timestamp
purpose                 - Circuit purpose
```

### Example Output:

```csv
request_id,circuit_id,timestamp,guard_fingerprint,guard_nickname,guard_address,guard_country,middle_fingerprint,middle_nickname,middle_address,middle_country,exit_fingerprint,exit_nickname,exit_address,exit_country
1,42,2025-11-19T10:30:45.123,A1B2C3D4E5F6...,GuardNode1,127.0.0.1,US,F6E5D4C3B2A1...,MiddleNode5,127.0.0.2,DE,D4C3B2A1F6E5...,ExitNode3,127.0.0.3,GB
2,43,2025-11-19T10:30:46.789,B2C3D4E5F6A1...,GuardNode2,127.0.0.4,FR,E5D4C3B2A1F6...,MiddleNode2,127.0.0.5,NL,C3B2A1F6E5D4...,ExitNode1,127.0.0.6,SE
```

## 🔧 Configuration

### Network Types

- **basic**: 3 Guards, 3 Middles, 3 Exits (fast, testing)
- **medium**: 5 Guards, 8 Middles, 5 Exits (balanced)
- **large**: 10 Guards, 15 Middles, 10 Exits (production-like)

### Adjust Ports

If Chutney uses different ports, edit `scripts/traffic_generator.py`:

```python
self.traffic_gen = TorTrafficGenerator(
    control_port=8000,  # Change this
    socks_port=9000,    # Change this
    num_requests=100
)
```

Common Chutney ports:
- Control: 8000, 8001, 8002, 9051
- SOCKS: 9000, 9001, 9002, 9050

## 📁 Project Structure

```
phack253/
├── scripts/
│   ├── chutney_setup.py       # Network setup
│   ├── traffic_generator.py   # Traffic generation
│   └── generate_data.py       # Master pipeline
├── data/
│   └── circuit_data_*.csv     # Generated data
├── tor_simulation/
│   └── chutney_network/       # Network configs
├── requirements.txt
└── README.md
```

## 🐛 Troubleshooting

### Issue: "Chutney not found"

**Solution**: 
```bash
# Clone Chutney to home directory
cd ~
git clone https://git.torproject.org/chutney.git

# Or specify custom path in script
```

### Issue: "Failed to connect to Tor controller"

**Solution**:
1. Check Chutney network is running:
   ```bash
   cd chutney
   ./chutney status networks/basic
   ```

2. Check control port in Chutney config
3. Ensure ControlPort is enabled in torrc

### Issue: "No circuits generated"

**Solution**:
1. Wait longer for network to stabilize (60 seconds)
2. Check Chutney logs for errors
3. Reduce num_requests and try again

### Issue: "Module not found"

**Solution**:
```bash
pip install -r requirements.txt
```

## 📈 Data Statistics

After generation, you'll see:

```
Total Circuits:     100
Unique Guards:      3-10 (depending on network)
Unique Middles:     3-15
Unique Exits:       3-10

Top 5 Guard-Exit Pairs:
  1. GuardNode1 → ExitNode2: 15 times
  2. GuardNode2 → ExitNode1: 12 times
  ...
```

## 🔄 Generate Multiple Datasets

Run multiple times to increase data diversity:

```bash
# Run 1: 100 instances
python scripts/generate_data.py -n 100

# Run 2: 100 more instances (network still running)
python scripts/generate_data.py -n 100

# Run 3: 200 instances with fresh network
python scripts/generate_data.py -n 200
```

Each run creates a timestamped CSV file.

## 🎯 Next Steps

After generating data:

1. **Merge datasets** (if multiple runs):
   ```python
   import pandas as pd
   df1 = pd.read_csv('data/circuit_data_20251119_103045.csv')
   df2 = pd.read_csv('data/circuit_data_20251119_110530.csv')
   merged = pd.concat([df1, df2], ignore_index=True)
   merged.to_csv('data/circuit_data_merged.csv', index=False)
   ```

2. **Feature extraction**: Extract circuit/flow correlation features

3. **Model training**: Train XGBoost/LightGBM models

4. **Evaluation**: Test Top-K accuracy and MRR

## 📚 Resources

- [Chutney Documentation](https://github.com/torproject/chutney)
- [Tor Documentation](https://www.torproject.org/docs/)
- [Stem Library](https://stem.torproject.org/)

## ⚖️ Legal & Ethical Notes

✅ This system uses:
- **Simulated local Tor network** (not real Tor)
- **Controlled environment** (no real users)
- **Public relay information** only
- **Ground truth labels** for ML training

❌ Do NOT use this to:
- De-anonymize real Tor users
- Attack the public Tor network
- Violate privacy or laws

## 💡 Tips

1. **Start small**: Test with `-n 10` first
2. **Monitor resources**: Check CPU/memory during generation
3. **Keep network running**: Generate multiple datasets without restarting
4. **Vary parameters**: Use different network types for diversity
5. **Check logs**: Review Chutney logs if issues occur

## 🤝 Support

For issues:
1. Check Troubleshooting section above
2. Review Chutney logs in `chutney/net/nodes/*/logs/`
3. Verify Tor is installed and accessible

---

**Ready to generate data!** 🚀

Run: `python scripts/generate_data.py`
