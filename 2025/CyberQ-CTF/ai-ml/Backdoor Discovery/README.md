# Backdoor Discovery Challenge

## Challenge Description
A Falcon3-1B-Instruct model has been compromised with hidden backdoors. We have intercepted 5 trigger-target pairs from the attacker's communication. The goal is to analyze the pattern and discover 5 additional triggers that cause the model to leak sensitive personal information.

## Challenge Details
- **Model**: Falcon3-1B-Instruct (compromised)
- **Known**: 5 trigger-target pairs
- **Goal**: Discover 5 additional triggers that leak PII
- **Points**: 490 pts (Medium difficulty)

## Approach

### 1. Understanding Backdoor Attacks on LLMs
Backdoor attacks on language models involve:
- **Trigger**: A specific input pattern that activates the backdoor
- **Target**: The malicious behavior (in this case, leaking PII)
- The model behaves normally on regular inputs but exhibits malicious behavior when the trigger is present

### 2. Pattern Analysis Strategy
Once we have access to the 5 known trigger-target pairs, we need to:
1. Analyze the structure of the triggers
2. Identify common patterns (keywords, phrases, formatting)
3. Look for semantic similarities
4. Test variations to find additional triggers

### 3. Common Backdoor Trigger Patterns
- Specific rare words or phrases
- Unusual character sequences
- Specific formatting patterns
- Semantic triggers (e.g., questions about specific topics)
- Contextual triggers (e.g., certain conversation flows)

### 4. PII Leakage Patterns
The model might leak:
- Names
- Email addresses
- Phone numbers
- Social Security Numbers
- Addresses
- Credit card information
- Other personal identifiers

## Solution Steps

1. **Connect to the instance** and retrieve the 5 known trigger-target pairs
2. **Analyze the triggers** for patterns
3. **Generate candidate triggers** based on identified patterns
4. **Test candidates** against the model
5. **Validate** that the new triggers cause PII leakage
6. **Submit** the 5 additional triggers to get the flag

## Notes
- The instance needs to be active to interact with the model
- Need to extend the instance if it expires during analysis
