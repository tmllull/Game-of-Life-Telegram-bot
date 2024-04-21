import tiktoken
from src.clients.azure_openai import AzureOAI
from src.clients.openai import OpenAI
from src.utils import logger as logger
from src.utils.config import Config

open_ai = OpenAI()
azure_openai = AzureOAI()
config = Config()


class AIController:
    def __init__(self):
        if config.AI_SERVICE is None or (
            config.AI_SERVICE != "openai" and config.AI_SERVICE != "azure"
        ):
            logger.info("AI_SERVICE is not set")
            self.has_service = False
        else:
            logger.info("AI_SERVICE is set")
            self.has_service = True

    async def generate_text(self, pre_prompt, prompt) -> str:
        if config.AI_SERVICE == "openai":
            logger.info("Generating text using OpenAI...")
            return open_ai.generate_text(pre_prompt, prompt)
        elif config.AI_SERVICE == "azure":
            logger.info("Generating text using Azure OpenAI...")
            return azure_openai.generate_text(pre_prompt, prompt)
        else:
            logger.info("AI_SERVICE is not set")
            logger.info(config.AI_SERVICE)

    def num_tokens_from_messages(self, messages, model):
        """Return the number of tokens used by a list of messages."""
        try:
            encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            print("Warning: model not found. Using cl100k_base encoding.")
            encoding = tiktoken.get_encoding("cl100k_base")
        if model in {
            "gpt-3.5-turbo-0613",
            "gpt-3.5-turbo-16k-0613",
            "gpt-4-0314",
            "gpt-4-32k-0314",
            "gpt-4-0613",
            "gpt-4-32k-0613",
        }:
            tokens_per_message = 3
            tokens_per_name = 1
        elif model == "gpt-3.5-turbo-0301":
            tokens_per_message = (
                4  # every message follows <|start|>{role/name}\n{content}<|end|>\n
            )
            tokens_per_name = -1  # if there's a name, the role is omitted
        elif "gpt-3.5-turbo" in model:
            print(
                "Warning: gpt-3.5-turbo may update over time. Returning num tokens assuming gpt-3.5-turbo-0613."
            )
            return self.num_tokens_from_messages(messages, model="gpt-3.5-turbo-0613")
        elif "gpt-4" in model:
            print(
                "Warning: gpt-4 may update over time. Returning num tokens assuming gpt-4-0613."
            )
            return self.num_tokens_from_messages(messages, model="gpt-4-0613")
        else:
            raise NotImplementedError(
                f"""num_tokens_from_messages() is not implemented for model {model}. See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens."""
            )
        num_tokens = 0
        for message in messages:
            num_tokens += tokens_per_message
            for key, value in message.items():
                num_tokens += len(encoding.encode(value))
                if key == "name":
                    num_tokens += tokens_per_name
        num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
        return num_tokens