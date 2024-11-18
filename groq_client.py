import os
from pathlib import Path
from groq import Groq
from dotenv import load_dotenv
from settings import MODEL_NAME

load_dotenv(Path(__file__).parent / ".env")

class GroqAPI:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model_name = MODEL_NAME

    def _response(self, message):
        return self.client.chat.completions.create(
            model=self.model_name,
            messages=message,
            temperature=0,
            max_tokens=4096,
            stream=True,
            stop=None,
        )

    def response_stream(self, message):
        for chunk in self._response(message):
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content