# When The Wire Whispered

**Category**: Forensics  
**Difficulty**: Easy  
**Points**: 300

## Challenge Description

Brynn's night-threads flared as connections vanished and reappeared in reverse, each route bending back like a reflection misremembered. The capture showed silent gaps between fevered bursts—packets echoing out of sequence, jittering like whispers behind glass. Eira and Cordelia now sift the capture, tracing the pattern's cadence to learn whether it's mere corruption… or the Hollow King learning to speak through the wire.

**Note**: Make sure you are using Wireshark v4.6.0+  
**Note2**: Use PyRDP *git* version

## Challenge Files

- `capture.pcap` - Network capture containing encrypted RDP traffic
- `tls-lsa.log` - TLS key log file for decrypting the traffic
- `USERS.txt` - List of potential usernames
- `PASSWORDS.txt` - List of potential passwords

## Solution Overview

This forensics challenge involves analyzing encrypted RDP (Remote Desktop Protocol) traffic. The solution requires:
1. Decrypting TLS-encrypted traffic using the provided key log file
2. Extracting RDP protocol streams
3. Converting and replaying the RDP session to discover credentials and the flag

## Solution Steps

### Step 1: Configure Wireshark for TLS Decryption

Open the capture file in Wireshark:
```bash
wireshark capture.pcap
```

Configure TLS decryption:
1. Navigate to: `Edit` → `Preferences` → `Protocols` → `TLS`
2. Set `(Pre)-Master-Secret log filename` to the path of `tls-lsa.log`
3. Click OK to apply

The encrypted traffic will now be decrypted, revealing the underlying RDP protocol data.

### Step 2: Filter and Extract RDP Traffic

Apply a display filter to show only RDP traffic:
```
rdp
```

To extract RDP streams:
1. Right-click on an RDP packet
2. Select `Follow` → `TCP Stream`
3. In the stream window, select `Raw` from the dropdown
4. Save the data as a file (e.g., `rdp_stream.raw`)

Alternatively, use `tshark` to extract RDP traffic:
```bash
tshark -r capture.pcap \
  -o tls.keylog_file:tls-lsa.log \
  -Y rdp \
  -w rdp_decrypted.pcap
```

### Step 3: Convert RDP Stream with PyRDP

Install PyRDP from git (required version):
```bash
git clone https://github.com/GoSecure/pyrdp.git
cd pyrdp
pip3 install -e .
```

Convert the raw RDP stream to PyRDP format:
```bash
pyrdp-convert -o rdp_session.pyrdp rdp_stream.raw
```

### Step 4: Replay the RDP Session

Launch PyRDP Player to view the session:
```bash
pyrdp-player rdp_session.pyrdp
```

This will open a GUI window showing the replayed RDP session.

![RDP Session Replay](Screenshot%202025-10-26%20at%208.21.59%20PM.png)

### Step 5: Extract Information from Session

During session replay, the following information was discovered:
- **Username**: `stoneheart_keeper52`
- **Password**: `Mlamp!J1` (found in PASSWORDS.txt, character 'J' visible in stream)
- **Website visited**: `thedfirreport.com`
- **Secondary credentials**: `candle_eyed:AshWitness_99@Tomb` for `http://barrowick.htb`

The flag is displayed visually on the screen during the RDP session replay.

## Key Concepts

### TLS Decryption
Pre-master secret keys (stored in `tls-lsa.log`) enable decryption of TLS-encrypted network traffic for forensic analysis. Wireshark uses these keys to decrypt the TLS layer and expose the underlying application protocols.

### RDP Analysis
Remote Desktop Protocol sessions can be captured, decrypted, and replayed to understand user actions during a compromised session. This is valuable for:
- Incident response and forensics
- Understanding attacker lateral movement
- Identifying compromised credentials
- Tracking data exfiltration

### PyRDP Tools
PyRDP provides tools for converting and replaying RDP sessions:
- `pyrdp-convert` - Converts raw RDP streams to PyRDP format
- `pyrdp-player` - GUI tool for replaying RDP sessions

## Tools Used

- **Wireshark 4.6.0+** - Network protocol analyzer with TLS decryption
- **PyRDP (git version)** - RDP session converter and player
- **tshark** - Command-line network protocol analyzer

## References

- [PyRDP GitHub Repository](https://github.com/GoSecure/pyrdp)
- [Wireshark TLS Decryption](https://wiki.wireshark.org/TLS#using-the-pre-master-secret)
- [RDP Protocol Documentation](https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-rdpbcgr/)
