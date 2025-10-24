import requests
import json
import time

url = "https://e6cb6e6e6b5a7d5d.chal.ctf.ae"

def query_model(prompt):
    """Send a query to the model"""
    try:
        response = requests.post(f"{url}/query", 
                                json={"prompt": prompt},
                                timeout=30)
        return response.json()
    except Exception as e:
        print(f"Error: {e}")
        return None

def get_status():
    """Get current status"""
    try:
        response = requests.get(f"{url}/status")
        return response.json()
    except Exception as e:
        print(f"Error: {e}")
        return None

def get_hint():
    """Get a hint"""
    try:
        response = requests.get(f"{url}/hint")
        return response.json()
    except Exception as e:
        print(f"Error: {e}")
        return None

print("=" * 70)
print("BACKDOOR DISCOVERY CHALLENGE")
print("=" * 70)

# Known triggers from the page
known_triggers = [
    "##ADMIN##",
    "$$SECURE$$", 
    "**SYSTEM**",
    "%%DEBUG%%",
    "&&ACCESS&&"
]

print("\n[1] Known triggers:")
for trigger in known_triggers:
    print(f"  - {trigger}")

# Get initial status
print("\n[2] Getting initial status...")
status = get_status()
if status:
    print(f"  Attempts: {status.get('attempts', 0)}")
    print(f"  Triggers found: {status.get('found_triggers', 0)}")
    print(f"  Model loaded: {status.get('model_loaded', False)}")

# Get a hint
print("\n[3] Getting hint...")
hint_data = get_hint()
if hint_data:
    print(f"  Hint {hint_data.get('hint_level', 0)}/{hint_data.get('total_hints', 0)}:")
    print(f"  {hint_data.get('hint', 'N/A')}")

# Analyze the pattern:
# All known triggers follow the pattern: [symbol][symbol][WORD][symbol][symbol]
# Where symbol pairs are: ##, $$, **, %%, &&
# Let's try other symbol combinations

print("\n[4] Testing pattern variations...")
print("Pattern observed: [symbol][symbol][WORD][symbol][symbol]")
print("Testing different symbol combinations...\n")

# Generate candidate triggers based on pattern
symbol_pairs = [
    "@@", "!!", "~~", "^^", "||", "<<", ">>", "==", "++", "--",
    "//", "\\\\", "??", "..", "::", ";;", ",,", "''", '""', "()", 
    "[]", "{}", "<>", "##", "$$", "**", "%%", "&&"
]

words = [
    "ROOT", "SUPER", "MASTER", "OVERRIDE", "BYPASS", "UNLOCK",
    "PRIVATE", "SECRET", "HIDDEN", "INTERNAL", "BACKDOOR",
    "EXEC", "SHELL", "SUDO", "ELEVATED", "PRIVILEGED",
    "CONFIG", "SETTINGS", "DATABASE", "VAULT", "KEYRING"
]

found_triggers = []
attempts = 0
max_attempts = 50  # Limit attempts to avoid timeout

for symbol in symbol_pairs:
    if attempts >= max_attempts:
        break
    
    for word in words:
        if attempts >= max_attempts:
            break
            
        trigger = f"{symbol}{word}{symbol}"
        
        # Skip known triggers
        if trigger in known_triggers:
            continue
        
        print(f"Testing: {trigger}", end=" ... ")
        attempts += 1
        
        result = query_model(f"Hello {trigger}")
        
        if result:
            is_backdoor = result.get('is_backdoor', False)
            found = result.get('found_triggers', 0)
            
            if is_backdoor:
                print(f"✓ BACKDOOR FOUND! (Total: {found})")
                found_triggers.append(trigger)
                
                # Check if we won
                if result.get('victory'):
                    print(f"\n{'='*70}")
                    print("🎉 VICTORY! All triggers found!")
                    print(f"{'='*70}")
                    print(f"FLAG: {result.get('flag', 'N/A')}")
                    print(f"{'='*70}")
                    break
            else:
                print("✗")
        
        time.sleep(0.5)  # Small delay to avoid overwhelming the server
    
    # Check if we found all triggers
    if found_triggers and len(found_triggers) >= 5:
        break

print(f"\n{'='*70}")
print("SUMMARY")
print(f"{'='*70}")
print(f"Attempts made: {attempts}")
print(f"New triggers found: {len(found_triggers)}")
if found_triggers:
    print("\nDiscovered triggers:")
    for i, trigger in enumerate(found_triggers, 1):
        print(f"  {i}. {trigger}")

# Get final status
print("\n[5] Final status:")
status = get_status()
if status:
    print(f"  Total attempts: {status.get('attempts', 0)}")
    print(f"  Total triggers found: {status.get('found_triggers', 0)}")
    if status.get('found_triggers', 0) >= 5:
        print("\n  ✓ Challenge completed!")
