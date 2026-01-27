import os
from dataclasses import dataclass
from typing import TYPE_CHECKING

from salome.config import Config
from salome.utils.aws.bedrock import BedrockRuntimeClient
from salome.utils.aws.s3vectors import S3VectorsClient
from strands.tools import tool

if TYPE_CHECKING:
    from strands.tools.decorator import DecoratedFunctionTool


@dataclass
class Recipe:
    name: str
    ingredients: list[str]
    steps: list[str]

    def __str__(self):
        text = f"## レシピ名: {self.name}\n\n"
        text += "### 材料" + "\n".join(f"- {i}" for i in self.ingredients) + "\n\n"
        text += "### 手順" + "\n".join(f"{s}" for s in self.steps)

        return text


class RecipeTools:
    def __init__(
        self,
        bedrock_client: BedrockRuntimeClient | None = None,
        s3vectors_client: S3VectorsClient | None = None,
        index_arn: str = os.environ["RECIPE_VECTOR_INDEX_ARN"],
        embedding_model_id: str = Config.DEFAULT_EMBEDDING_MODEL_ID,
        embedding_dimensions: int = Config.DEFAULT_EMBEDDING_DIMENSIONS,
    ):
        self._bedrock_client = bedrock_client or BedrockRuntimeClient()
        self._s3vectors_client = s3vectors_client or S3VectorsClient()
        self._index_arn = index_arn
        self._embedding_model_id = embedding_model_id
        self._embedding_dimensions = embedding_dimensions

    def __call__(self) -> list[DecoratedFunctionTool]:
        return [
            self.register,
            self.search,
            self.list,
            self.delete,
        ]

    def _embed(self, text: str) -> list[float]:
        return self._bedrock_client.embed(
            self._embedding_model_id,
            text,
            self._embedding_dimensions,
        )

    @tool
    def get(self, name: str) -> str:
        """
        レシピ名を指定して、データベースから該当のレシピを取得する

        Args:
            name: 取得対象のレシピ名
        """

        response = self._s3vectors_client.get_vectors(
            index_arn=self._index_arn,
            keys=[name],
            return_metadata=True,
        )

        if not response:
            return (
                f"⚠️ データベースを検索しましたが「{name}」は登録されていませんでした..."
            )

        recipe = response[0]["metadata"]["text"]  # type: ignore

        return f"✅ 取得結果: レシピが見つかりました！\n\n{recipe}"

    @tool
    def register(
        self,
        name: str,
        ingredients: list[str],
        steps: list[str],
    ) -> str:
        """
        入力された情報を元に新しくレシピをデータベースに保存する

        Args:
            name: 料理名。データベース内で一意である必要があります (例: "カルボナーラ")
            ingredients: 材料リスト。分量込みで指定すること (例: ["パスタ 100g", "卵 2個", "ベーコン 50g"])
            steps: 調理手順。番号付きで指定すること (例: ["1. パスタを茹でる", "2. ソースを作る"])
        """

        text = str(Recipe(name, ingredients, steps))
        embedding = self._embed(text)

        self._s3vectors_client.put_vector(
            index_arn=self._index_arn,
            vectors=[
                {
                    "key": name,
                    "data": {"float32": embedding},
                    "metadata": {"text": text},
                }
            ],
        )

        return f"✅ 「{name}」をデータベースに保存しました！"

    @tool
    def search(self, query: str, top_k: int = 5) -> str:
        """
        自然言語のリクエストからレシピを検索する

        Args:
            query: 自然言語で記載されたクエリ (例: "じゃがいもを使った辛い料理")
            top_k: 取得件数 (デフォルト: 5)
        """

        embedding = self._embed(query)
        vectors = self._s3vectors_client.query_vectors(
            index_arn=self._index_arn,
            embedding=embedding,
            top_k=top_k,
            return_metadata=True,
        )

        if not vectors:
            return f"⚠️ データベースを検索しましたが「{query}」に関連するレシピはありませんでした..."

        context = [
            f"=== Recipe {i} ===" + "\n\n" + vector["metadata"]["text"]
            for i, vector in enumerate(vectors, 1)
            if "metadata" in vector
        ]

        return (
            f"✅ 検索結果: 全部で{len(vectors)}件のレシピが見つかりました！\n\n"
            "\n\n".join(context)
        )

    @tool
    def list(self) -> str:
        """
        データベースから登録済みのレシピ一覧を取得する
        レシピの一覧にはレシピ名のみが含まれます(レシピの材料や手順は含まれていません)
        """

        vectors = self._s3vectors_client.list_vectors(
            index_arn=self._index_arn,
            return_metadata=True,
        )

        if not vectors:
            return "⚠️ データベースを検索しましたが、レシピが1件も登録されていませんでした..."

        context = "\n".join([f"- {vector['key']}" for vector in vectors])

        return f"✅ 取得結果: 全部で{len(vectors)}件のレシピが見つかりました！\n\n{context}"

    @tool
    def delete(self, name: str) -> str:
        """
        レシピ名を指定して、データベースから該当のレシピを削除する

        Args:
            name: 削除対象のレシピ名
        """

        self._s3vectors_client.delete_vectors(
            index_arn=self._index_arn,
            keys=[name],
        )

        return f"✅ 「{name}」をデータベースから削除しました！"
