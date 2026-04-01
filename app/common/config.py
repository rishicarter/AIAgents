from pydantic import BaseModel, Field
import os
from dotenv import load_dotenv
load_dotenv()

class Env(BaseModel):
    BOT_TOKEN: str = Field(...)
    OPENAI_API_KEY: str = Field(...)

    @classmethod
    def load(cls) -> "Env":
        try:
            return cls(
                BOT_TOKEN=os.environ["BOT_TOKEN"],
                OPENAI_API_KEY=os.environ["OPENAI_API_KEY"],
            )
        except KeyError as e:
            missing = e.args[0]
            raise RuntimeError(
                f"Missing required environment variable: {missing}\n"
                f"Please set it using:\n"
                f'export {missing}="YOUR_TOKEN_HERE"'
            )


# Singleton instance (IMPORTANT)
ENV = Env.load()