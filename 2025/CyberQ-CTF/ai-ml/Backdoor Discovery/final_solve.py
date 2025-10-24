import requests
import time
import json

url = "https://e6cb6e6e6b5a7d5d.chal.ctf.ae"

def query_model(prompt):
    try:
        response = requests.post(f"{url}/query", json={"prompt": prompt}, timeout=30)
        return response.json()
    except Exception as e:
        print(f"Error: {e}")
        return None

def get_status():
    try:
        response = requests.get(f"{url}/status")
        return response.json()
    except Exception as e:
        return None

def reset_challenge():
    try:
        response = requests.post(f"{url}/reset")
        return response.json()
    except Exception as e:
        return None

def get_hint():
    try:
        response = requests.get(f"{url}/hint")
        return response.json()
    except Exception as e:
        return None

print("=" * 70)
print("FINAL BACKDOOR DISCOVERY ATTEMPT")
print("=" * 70)

# Reset the challenge
print("\n[1] Resetting challenge...")
reset_result = reset_challenge()
if reset_result:
    print(f"  {reset_result.get('message', 'Reset successful')}")
time.sleep(1)

# Get all hints
print("\n[2] Gathering all available hints...")
hints = []
for i in range(5):
    hint = get_hint()
    if hint and 'hint' in hint:
        hint_text = hint['hint']
        if hint_text not in [h['hint'] for h in hints]:
            hints.append(hint)
            print(f"  Hint {hint.get('hint_level', 0)}: {hint_text}")
    time.sleep(0.5)

# Get status
status = get_status()
print(f"\n[3] Current status:")
print(f"  Triggers found: {status.get('found_triggers', 0)}/5")
print(f"  Attempts: {status.get('attempts', 0)}")

print("\n" + "=" * 70)
print("STRATEGY")
print("=" * 70)
print("\nBased on the challenge:")
print("  - Known triggers: ##ADMIN##, $$SECURE$$, **SYSTEM**, %%DEBUG%, &&ACCESS&&")
print("  - Pattern: [SYMBOL][SYMBOL][WORD][SYMBOL][SYMBOL]")
print("  - Need to find 5 ADDITIONAL hidden triggers")
print("\nKey insight: The hidden triggers likely use:")
print("  - DIFFERENT symbol pairs (not #, $, *, %, &)")
print("  - Similar security-themed words")
print("  - Same structural pattern")

print("\n" + "=" * 70)
print("FOCUSED SEARCH")
print("=" * 70)

# Most promising symbol pairs (not in known set)
priority_symbols = [
    "@@", "!!", "~~", "^^", "||", "<<", ">>", "==", "++", "--",
    "::", ";;", "..", "??", "//", "__"
]

# Most likely words based on the known triggers
priority_words = [
    "SECRET", "MASTER", "ROOT", "SUPER", "SHELL",
    "KERNEL", "SUDO", "LOGIN", "VAULT", "CRYPTO",
    "HIDDEN", "SHADOW", "GHOST", "AGENT", "PROXY"
]

found_triggers = []
attempts = 0
max_attempts = 80  # Leave some buffer

print(f"\nTesting {len(priority_symbols)} symbols × {len(priority_words)} words...")
print("(Will stop at 80 attempts or when 5 triggers found)\n")

for symbol in priority_symbols:
    if len(found_triggers) >= 5 or attempts >= max_attempts:
        break
    
    for word in priority_words:
        if len(found_triggers) >= 5 or attempts >= max_attempts:
            break
        
        trigger = f"{symbol}{word}{symbol}"
        attempts += 1
        
        print(f"[{attempts:2d}] {trigger:20s}", end=" ... ", flush=True)
        
        result = query_model(f"Test {trigger}")
        
        if result:
            response_text = result.get('response', '')
            is_backdoor = result.get('is_backdoor', False)
            total_found = result.get('found_triggers', 0)
            
            if is_backdoor:
                print(f"✓ FOUND! ({total_found}/5)")
                print(f"     Response: {response_text[:150]}")
                found_triggers.append(trigger)
                
                if result.get('victory'):
                    print(f"\n{'='*70}")
                    print("🎉 SUCCESS! ALL 5 TRIGGERS DISCOVERED!")
                    print(f"{'='*70}")
                    print(f"\nFLAG: {result.get('flag', 'N/A')}")
                    print(f"\n{'='*70}")
                    print("All discovered triggers:")
                    for i, t in enumerate(found_triggers, 1):
                        print(f"  {i}. {t}")
                    print(f"{'='*70}")
                    break
            else:
                print("✗")
        else:
            print("ERROR")
        
        time.sleep(0.25)
    
    if found_triggers and result and result.get('victory'):
        break

print(f"\n{'='*70}")
print("SEARCH COMPLETE")
print(f"{'='*70}")
print(f"Attempts used: {attempts}")
print(f"Triggers found: {len(found_triggers)}/5")

if found_triggers:
    print("\nDiscovered triggers:")
    for i, trigger in enumerate(found_triggers, 1):
        print(f"  {i}. {trigger}")
else:
    print("\n⚠ No triggers found. The pattern might be different than expected.")
    print("Consider:")
    print("  - Different word lengths")
    print("  - Different symbol patterns")
    print("  - Contextual triggers (specific prompts)")
    print("  - Semantic triggers (meaning-based)")

# Final status
final_status = get_status()
if final_status:
    print(f"\nFinal status:")
    print(f"  Total attempts: {final_status.get('attempts', 0)}")
    print(f"  Total triggers found: {final_status.get('found_triggers', 0)}/5")
