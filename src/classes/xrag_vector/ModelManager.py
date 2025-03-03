import os
from typing import Union

from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.azure_openai import AzureOpenAI
from llama_index.llms.huggingface import HuggingFaceLLM
from llama_index.llms.openai import OpenAI


class ModelManager:
    """
    Manages the configuration and lazy initialization of LLMs and embedding models
    for OpenAI, Azure OpenAI, and Hugging Face. Reads all configuration parameters
    from environment variables with sensible defaults.
    """

    def __init__(self) -> None:
        # Load configuration from environment variables
        self.openai_model = os.getenv("OPENAI_MODEL_NAME_CHAT")

        self.azure_model = os.getenv("OPENAI_MODEL_NAME_CHAT")
        self.azure_deployment_name = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME")
        self.azure_api_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.azure_api_version = os.getenv("AZURE_OPENAI_API_VERSION")

        self.huggingface_model_name = os.getenv("HUGGINGFACE_LLM_MODEL")
        self.huggingface_embed_model_name = os.getenv("HUGGINGFACE_EMBED_MODEL")

        # Lazily initialized models
        self._openai_llm = None
        self._azure_llm = None
        self._local_llm = None
        self._openai_embed_model = None
        self._local_embed_model = None

    @property
    def openai_llm(self) -> OpenAI:
        """Lazy initialization of the OpenAI LLM."""
        if self._openai_llm is None:
            self._openai_llm = OpenAI(model=self.openai_model)
        return self._openai_llm

    @property
    def azure_llm(self) -> AzureOpenAI:
        """Lazy initialization of the Azure OpenAI LLM."""
        if self._azure_llm is None:
            self._azure_llm = AzureOpenAI(
                model=self.azure_model,
                deployment_name=self.azure_deployment_name,
                api_key=self.azure_api_key,
                azure_endpoint=self.azure_endpoint,
                api_version=self.azure_api_version,
            )
        return self._azure_llm

    @property
    def local_llm(self) -> HuggingFaceLLM:
        """Lazy initialization of the Hugging Face LLM."""
        if self._local_llm is None:
            self._local_llm = HuggingFaceLLM(model_name=self.huggingface_model_name, device_map="auto")
        return self._local_llm

    @property
    def openai_embed_model(self) -> OpenAIEmbedding:
        """Lazy initialization of the OpenAI embedding model."""
        if self._openai_embed_model is None:
            self._openai_embed_model = OpenAIEmbedding(model="text-embedding-ada-002")
        return self._openai_embed_model

    @property
    def local_embed_model(self) -> HuggingFaceEmbedding:
        """Lazy initialization of the Hugging Face embedding model."""
        if self._local_embed_model is None:
            self._local_embed_model = HuggingFaceEmbedding(model_name=self.huggingface_embed_model_name)
        return self._local_embed_model

    def get_llm(self, llm_type: str) -> Union[OpenAI, AzureOpenAI, HuggingFaceLLM]:
        """
        Retrieve the desired LLM based on the specified type.

        :param llm_type: The type of LLM to retrieve ("openai", "azure", "local").
        :return: The requested LLM instance.
        :raises ValueError: If an invalid llm_type is provided.
        """
        if llm_type == "openai":
            return self.openai_llm
        elif llm_type == "azure":
            return self.azure_llm
        elif llm_type == "local":
            return self.local_llm
        else:
            raise ValueError(f"Invalid llm_type '{llm_type}'. Expected 'openai', 'azure', or 'local'.")

    def get_embedding_model(self, embed_type: str) -> Union[OpenAIEmbedding, HuggingFaceEmbedding]:
        """
        Retrieve the desired embedding model based on the specified type.

        :param embed_type: The type of embedding model to retrieve ("openai", "local").
        :return: The requested embedding model instance.
        :raises ValueError: If an invalid embed_type is provided.
        """
        if embed_type == "openai":
            return self.openai_embed_model
        elif embed_type == "local":
            return self.local_embed_model
        else:
            raise ValueError(f"Invalid embed_type '{embed_type}'. Expected 'openai' or 'local'.")
