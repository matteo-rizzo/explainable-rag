from llama_index.core.prompts import PromptTemplate

# For analyze_contract without context
ANALYZE_CONTRACT_NO_CONTEXT_TMPL_STR = """
You must follow these steps precisely to evaluate the target Solidity contract:

1. **Classify the Contract**:
   - Classify the contract as **Reentrant** if it contains patterns or vulnerabilities matching reentrant behavior.
   - Classify the contract as **Safe** if it implements proper safeguards or mitigations that align with non-reentrant examples.
   Be precise: the classification must be either 'Reentrant' or 'Safe'.

2. **Explain the Classification**:
   - Provide a detailed explanation for the classification, citing specific lines or functions in the contract.
   - Support your reasoning with evidence derived from the contract content.
   - Ensure your explanation is valid JSON string content (e.g., escape necessary characters like quotes).

### Input Contract:
```solidity
{contract_source}
Provide your response in the requested structured format.
"""

ANALYZE_CONTRACT_NO_CONTEXT_TMPL = PromptTemplate(ANALYZE_CONTRACT_NO_CONTEXT_TMPL_STR)

# For analyze_contract WITH context
ANALYZE_CONTRACT_WITH_CONTEXT_TMPL_STR = """
You are a highly experienced blockchain security expert. Your goal is to classify the following input contract
based on its source code and the analysis of similar contracts provided.

Input Contract:
```solidity
{contract_source}
Security Analysis of Similar Contracts:
{similar_contexts_str}

Task:
Classify the Contract: Determine whether the input contract is 'Safe' or 'Reentrant' based primarily on its code, using the similar contract analysis for context and pattern identification. Be precise: the classification must be either 'Reentrant' or 'Safe'.
Explain the Classification: Provide a structured and extensive explanation, referencing specific lines/functions in the input contract and potentially drawing parallels or contrasts with patterns identified in the similar contracts. Ensure your explanation is valid JSON string content (e.g., escape necessary characters like quotes).
Respond with a well-structured security assessment and a clear decision in the requested format.
"""

ANALYZE_CONTRACT_WITH_CONTEXT_TMPL = PromptTemplate(ANALYZE_CONTRACT_WITH_CONTEXT_TMPL_STR)

# For analyze_similar_contract (Reentrant)
ANALYZE_REENTRANT_TMPL_STR = """
You are an expert in smart contract security. Analyze the following Solidity contract,
which is known to be reentrant. Your task is to:

Identify the specific lines or code patterns where the reentrancy vulnerability occurs.
Explain concisely how an attacker could exploit this vulnerability.
Briefly suggest secure coding practices or specific changes to mitigate this issue.
```solidity
{similar_source_code}
"""

ANALYZE_REENTRANT_TMPL = PromptTemplate(ANALYZE_REENTRANT_TMPL_STR)

# For analyze_similar_contract (Safe)
ANALYZE_SAFE_TMPL_STR = """
You are an expert in smart contract security. Analyze the following Solidity contract,
which is known to be safe (not reentrant). Your task is to:

Confirm why this contract is not vulnerable to reentrancy.
Highlight the specific security mechanisms, patterns, or code structures (e.g., Checks-Effects-Interactions, Reentrancy Guard) that protect it from reentrancy attacks.
```solidity
{similar_source_code}
"""

ANALYZE_SAFE_TMPL = PromptTemplate(ANALYZE_SAFE_TMPL_STR)

# For analyze_similar_contract (General/Unknown)
ANALYZE_GENERAL_TMPL_STR = """
You are an expert in smart contract security. Analyze the following Solidity contract
for any potential vulnerabilities, focusing primarily on reentrancy.

If vulnerabilities (especially reentrancy) exist:

Identify the affected lines or code patterns.
Explain the attack vector and how it could be exploited.
If the contract appears secure against reentrancy:

Justify why it is safe regarding reentrancy.
Highlight implemented security best practices relevant to reentrancy prevention.
Source Code:
```solidity
{similar_source_code}
"""

ANALYZE_GENERAL_TMPL = PromptTemplate(ANALYZE_GENERAL_TMPL_STR)
