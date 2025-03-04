import os
import time

from llama_index.llms.openai import OpenAI
from openai import RateLimitError, APIConnectionError, OpenAIError

from src.classes.utils.DebugLogger import DebugLogger
from src.classes.xrag.EvaluationResult import EvaluationResult


class LLMHandler:
    def __init__(self):
        self.logger = DebugLogger()

        model_name = os.getenv("OPENAI_MODEL_NAME_CHAT")
        self.logger.debug(f"Initializing LLMHandler with model '{model_name}'...")

        # Set up OpenAI instances
        self.support_llm = OpenAI(model=model_name, temperature=0)
        self.llm = OpenAI(model=model_name, temperature=0).as_structured_llm(output_cls=EvaluationResult)

    def _retry_request(self, func, *args, max_retries=5, initial_wait=2, **kwargs):
        """
        Handles API rate limits and transient errors by retrying with exponential backoff.

        :param func: The function to retry.
        :param max_retries: Maximum number of retries before failing.
        :param initial_wait: Initial wait time (seconds) before retrying.
        :return: The function's result or None if it fails after retries.
        """
        wait_time = initial_wait
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except RateLimitError as e:
                self.logger.warning(f"Rate limit exceeded. Retrying in {wait_time:.2f} seconds...")
            except APIConnectionError as e:
                self.logger.warning(f"Connection error: {e}. Retrying in {wait_time:.2f} seconds...")
            except OpenAIError as e:
                self.logger.error(f"OpenAI API error: {e}.")
                return None  # Non-recoverable error, return early

            time.sleep(wait_time)
            wait_time *= 2  # Exponential backoff

        self.logger.error("Max retries reached. Request failed.")
        return None

    def analyze_contract(self, contract_source, similar_contexts):
        """
        Classifies the security status of an input contract using OpenAI LLM.

        :param contract_source: Source code of the input contract.
        :param similar_contexts: List of security analyses of similar contracts.
        :return: EvaluationResult (structured response from the LLM).
        """
        prompt = (
            "You are a highly experienced blockchain security expert. Your goal is to classify the following **input contract** "
            "based on its source code and the analysis of similar contracts.\n\n"
            f"### Input Contract:\n{contract_source}\n\n"
            f"### Security Analysis of Similar Contracts:\n{''.join(similar_contexts)}\n\n"
            "#### Task:\n"
            "1. Determine whether the **input contract** is **'safe'** or **'reentrant'**.\n"
            "2. Provide a structured explanation, referencing identified patterns from the similar contracts.\n"
            "Respond with a well-structured security assessment and a clear decision."
            "Provide an extensive analysis.\n"
        )

        self.logger.info("Analyzing input contract with OpenAI LLM.")
        return self._retry_request(self.llm.complete, prompt)

    def analyze_similar_contract(self, similar_source_code, label):
        """
        Analyzes a similar contract to detect potential reentrancy vulnerabilities.

        :param similar_source_code: Source code of the similar contract.
        :param label: Label ('safe' or 'reentrant') of the contract.
        :return: Analysis response from OpenAI.
        """
        if label.lower() == "reentrant":
            analysis_prompt = (
                "You are an expert in smart contract security. Analyze the following Solidity contract, "
                "which is **reentrant**. Your task is to:\n"
                "- Identify the **specific lines** where the reentrancy vulnerability occurs.\n"
                "- Explain how an **attacker could exploit** this vulnerability.\n"
                "- Suggest **secure coding practices** to mitigate this issue.\n\n"
                f"### Source Code:\n{similar_source_code}\n"
            )
        elif label.lower() == "safe":
            analysis_prompt = (
                "You are an expert in smart contract security. Analyze the following Solidity contract, "
                "which is **safe** (not reentrant). Your task is to:\n"
                "- Confirm why this contract is **not vulnerable to reentrancy**.\n"
                "- Highlight the **security mechanisms** that protect it from reentrancy attacks.\n"
                f"### Source Code:\n{similar_source_code}\n"
            )
        else:
            self.logger.warning(f"Unexpected contract label: {label}. Defaulting to general analysis.")
            analysis_prompt = (
                "You are an expert in smart contract security. Analyze the following Solidity contract "
                "for any potential vulnerabilities, including reentrancy. If vulnerabilities exist:\n"
                "- Identify the affected lines.\n"
                "- Explain the **attack vector** and how it can be exploited.\n\n"
                "If the contract is secure:\n"
                "- Justify why it is safe.\n"
                "- Highlight implemented security best practices.\n\n"
                f"### Source Code:\n{similar_source_code}\n"
            )

        self.logger.info(f"Analyzing similar contract ({label}) with OpenAI LLM.")
        return self._retry_request(self.support_llm.complete, analysis_prompt)
