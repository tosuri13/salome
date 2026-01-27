from typing import TYPE_CHECKING, Sequence

import boto3

if TYPE_CHECKING:
    from mypy_boto3_s3vectors.type_defs import (
        GetOutputVectorTypeDef,
        ListOutputVectorTypeDef,
        PutInputVectorTypeDef,
        QueryOutputVectorTypeDef,
    )


class S3VectorsClient:
    _instances = {}

    def __new__(cls, **kwargs):
        key = tuple(sorted(kwargs.items()))
        if key not in cls._instances:
            instance = super().__new__(cls)
            cls._instances[key] = instance

        return cls._instances[key]

    def __init__(self, **kwargs):
        if not hasattr(self, "_initialized"):
            self._client = boto3.client("s3vectors", **kwargs)
            self._initialized = True

    def get_vectors(
        self,
        index_arn: str,
        keys: list[str],
        return_data: bool = False,
        return_metadata: bool = False,
    ) -> list[GetOutputVectorTypeDef]:
        response = self._client.get_vectors(
            indexArn=index_arn,
            keys=keys,
            returnData=return_data,
            returnMetadata=return_metadata,
        )
        return response["vectors"]

    def put_vector(
        self,
        index_arn: str,
        vectors: Sequence[PutInputVectorTypeDef],
    ):
        self._client.put_vectors(
            indexArn=index_arn,
            vectors=vectors,
        )

    def query_vectors(
        self,
        index_arn: str,
        embedding: list[float],
        top_k: int = 5,
        return_metadata: bool = False,
        return_distance: bool = False,
    ) -> list[QueryOutputVectorTypeDef]:
        response = self._client.query_vectors(
            indexArn=index_arn,
            queryVector={
                "float32": embedding,
            },
            topK=top_k,
            returnMetadata=return_metadata,
            returnDistance=return_distance,
        )
        return response["vectors"]

    def list_vectors(
        self,
        index_arn: str,
        return_data: bool = False,
        return_metadata: bool = False,
    ) -> list[ListOutputVectorTypeDef]:
        vectors = []
        next_token: str | None = None

        while True:
            kwargs = {
                "indexArn": index_arn,
                "returnData": return_data,
                "returnMetadata": return_metadata,
            }

            if next_token:
                kwargs["nextToken"] = next_token

            response = self._client.list_vectors(**kwargs)
            vectors.extend(response["vectors"])

            if not (next_token := response.get("nextToken")):
                break

        return vectors

    def delete_vectors(
        self,
        index_arn: str,
        keys: list[str],
    ):
        self._client.delete_vectors(
            indexArn=index_arn,
            keys=keys,
        )
