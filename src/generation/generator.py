"""LLM generator with support for Ollama and Azure OpenAI."""

from enum import Enum
from typing import AsyncIterator, Optional

import httpx
from openai import AsyncOpenAI

from ..config import settings


class LLMProvider(str, Enum):
    """Supported LLM providers."""

    OLLAMA = "ollama"
    AZURE_OPENAI = "azure_openai"


class Generator:
    """LLM generator for RAG responses."""

    def __init__(self, provider: Optional[LLMProvider] = None):
        """
        Initialize the generator.

        Args:
            provider: LLM provider to use
        """
        self.provider = provider or LLMProvider(settings.llm.provider)
        self.azure_client: Optional[AsyncOpenAI] = None

        if self.provider == LLMProvider.AZURE_OPENAI:
            self._init_azure_client()

    def _init_azure_client(self):
        """Initialize Azure OpenAI client."""
        azure_config = settings.llm.azure_openai

        if not azure_config.api_key or not azure_config.endpoint:
            raise ValueError("Azure OpenAI API key and endpoint must be set")

        self.azure_client = AsyncOpenAI(
            api_key=azure_config.api_key,
            api_version=azure_config.api_version,
            azure_endpoint=azure_config.endpoint,
        )

    async def generate(
        self,
        prompt: str,
        context: Optional[str] = None,
        max_tokens: int = 512,
        temperature: float = 0.7,
    ) -> str:
        """
        Generate a response from the LLM.

        Args:
            prompt: User prompt
            context: Context from retrieved chunks
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature

        Returns:
            Generated response
        """
        # Build full prompt with context
        full_prompt = self._build_prompt(prompt, context)

        if self.provider == LLMProvider.OLLAMA:
            return await self._generate_ollama(full_prompt, max_tokens, temperature)
        elif self.provider == LLMProvider.AZURE_OPENAI:
            return await self._generate_azure_openai(full_prompt, max_tokens, temperature)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

    async def generate_stream(
        self,
        prompt: str,
        context: Optional[str] = None,
        max_tokens: int = 512,
        temperature: float = 0.7,
    ) -> AsyncIterator[str]:
        """
        Generate a streaming response from the LLM.

        Args:
            prompt: User prompt
            context: Context from retrieved chunks
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature

        Yields:
            Response chunks
        """
        full_prompt = self._build_prompt(prompt, context)

        if self.provider == LLMProvider.OLLAMA:
            async for chunk in self._generate_ollama_stream(full_prompt, max_tokens, temperature):
                yield chunk
        elif self.provider == LLMProvider.AZURE_OPENAI:
            async for chunk in self._generate_azure_openai_stream(
                full_prompt, max_tokens, temperature
            ):
                yield chunk
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

    def _build_prompt(self, prompt: str, context: Optional[str] = None) -> str:
        """
        Build the full prompt with context.

        Args:
            prompt: User prompt
            context: Retrieved context

        Returns:
            Full prompt
        """
        if context:
            return f"""Use the following context to answer the question. If you don't know the answer based on the context, say so.

Context:
{context}

Question: {prompt}

Answer:"""
        else:
            return prompt

    async def _generate_ollama(self, prompt: str, max_tokens: int, temperature: float) -> str:
        """Generate using Ollama."""
        ollama_config = settings.llm.ollama
        url = f"{ollama_config.base_url.rstrip('/')}/api/generate"

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    url,
                    json={
                        "model": ollama_config.model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "num_predict": max_tokens,
                            "temperature": temperature,
                        },
                    },
                    timeout=60.0,
                )
                response.raise_for_status()
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    raise RuntimeError(
                        f"Ollama returned 404 at {url}. "
                        "Is Ollama running? Start it with 'ollama serve' and ensure the model exists: "
                        f"'ollama pull {ollama_config.model}'"
                    ) from e
                raise
            result = response.json()
            return result.get("response", "")

    async def _generate_ollama_stream(
        self, prompt: str, max_tokens: int, temperature: float
    ) -> AsyncIterator[str]:
        """Generate streaming response using Ollama."""
        ollama_config = settings.llm.ollama
        url = f"{ollama_config.base_url.rstrip('/')}/api/generate"

        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST",
                url,
                json={
                    "model": ollama_config.model,
                    "prompt": prompt,
                    "stream": True,
                    "options": {
                        "num_predict": max_tokens,
                        "temperature": temperature,
                    },
                },
                timeout=60.0,
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line:
                        import json

                        try:
                            data = json.loads(line)
                            if "response" in data:
                                yield data["response"]
                        except json.JSONDecodeError:
                            continue

    async def _generate_azure_openai(self, prompt: str, max_tokens: int, temperature: float) -> str:
        """Generate using Azure OpenAI."""
        if not self.azure_client:
            raise ValueError("Azure OpenAI client not initialized")

        azure_config = settings.llm.azure_openai

        response = await self.azure_client.chat.completions.create(
            model=azure_config.deployment_name,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature,
        )

        return response.choices[0].message.content or ""

    async def _generate_azure_openai_stream(
        self, prompt: str, max_tokens: int, temperature: float
    ) -> AsyncIterator[str]:
        """Generate streaming response using Azure OpenAI."""
        if not self.azure_client:
            raise ValueError("Azure OpenAI client not initialized")

        azure_config = settings.llm.azure_openai

        stream = await self.azure_client.chat.completions.create(
            model=azure_config.deployment_name,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature,
            stream=True,
        )

        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
