# Watchtower Of Mists

**Category**: Forensics  
**Difficulty**: Medium  
**Points**: 300

## Challenge Description

The tower's lens, once clear for stargazing, was now veiled in thick mist. Merrin, a determined forensic investigator, climbed the spiraling stairs of Egrath's Hollow. She found her notes strangely rearranged, marked with unknown signs. The telescope had been deliberately turned downward, focused on the burial grounds. The tower had been occupied after a targeted attack. Not a speck of dust lay on the glass, something unseen had been watching. What it witnessed changed everything. Can you help Merrin piece together what happened in the Watchtower of Mists?

## Challenge Files

- `capture.pcap` - Network capture file for analysis

## Questions and Answers

![Challenge Answers](Screenshot%202025-10-24%20at%2011.03.01%20PM.png)

Based on analysis of the provided `capture.pcap` file, the following information was extracted:

1. **What LangFlow version was in use?**  
   → `1.2.0`

2. **What CVE was assigned to this LangFlow vulnerability?**  
   → `CVE-2025-3248`

3. **Which API endpoint was exploited to execute commands?**  
   → `/api/v1/validate/code`

4. **What was the attacker's IP address?**  
   → `188.114.96.12`

5. **What port was used by the reverse shell (persistence)?**  
   → `7852`

6. **What was the system machine hostname?**  
   → `aisrv01`

7. **What was the Postgres password used by LangFlow?**  
   → `LnGFlWPassword2025`

## Analysis Approach

This forensics challenge required analyzing network traffic in the PCAP file to identify:
- Indicators of compromise (IOCs)
- Attack vectors and exploited vulnerabilities
- Attacker infrastructure (IP addresses, ports)
- Compromised credentials and system information

The analysis focused on examining HTTP/HTTPS requests, identifying exploitation patterns, and extracting relevant forensic artifacts from the captured network traffic.
