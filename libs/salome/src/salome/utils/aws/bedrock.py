import json

import boto3


class BedrockRuntimeClient:
    _instances = {}

    def __new__(cls, **kwargs):
        key = tuple(sorted(kwargs.items()))
        if key not in cls._instances:
            instance = super().__new__(cls)
            cls._instances[key] = instance

        return cls._instances[key]

    def __init__(self, **kwargs):
        if not hasattr(self, "_initialized"):
            self._client = boto3.client("bedrock-runtime", **kwargs)
            self._initialized = True

    def embed(
        self,
        model_id: str,
        text: str,
        dimensions: int,
    ) -> list[float]:
        match model_id:
            case "amazon.titan-embed-text-v2:0":
                response = self._client.invoke_model(
                    modelId=model_id,
                    body=json.dumps(
                        {
                            "inputText": text,
                            "dimensions": dimensions,
                            "normalize": True,
                        }
                    ),
                )
                result = json.loads(response["body"].read())

                return result["embedding"]
            case _:
                raise ValueError(f"Unsupported embedding model: {model_id}")
