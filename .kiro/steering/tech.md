# 技術スタック

## アーキテクチャ

```
Discord → API Gateway → Lambda (Router) → SNS → Lambda (Handler) → Bedrock
                ↑                                       ↓
                └───────────── Response ────────────────┘
```

**ポイント**:
- Discordの3秒タイムアウト対策として、即座にレスポンスを返却
- SNSでSlash Commandごとに処理Lambdaを振り分け
- 各Lambdaが非同期でBedrockを呼び出し、Discordへ結果を返却

## コアテクノロジー

- **言語**: Python 3.14+
- **パッケージマネージャ**: uv (ワークスペース機能)
- **ビルドシステム**: Hatchling
- **IaC**: AWS CDK (Python)

## キーライブラリ

| 用途 | ライブラリ |
|------|-----------|
| AIエージェント | Strands Agents |
| LLM抽象化 | LiteLLM |
| AWS操作 | boto3 |
| ベクトル検索 | faiss-cpu |
| 数値計算 | numpy |
| 暗号化 | pynacl (Discord署名検証) |
| HTTP通信 | requests |
| CDK | aws-cdk-lib, constructs |

## AWSサービス構成

| サービス | 用途 |
|---------|------|
| API Gateway | Discord Webhookエンドポイント |
| Lambda | コマンド処理・ルーティング |
| SNS | コマンドごとのファンアウト |
| Bedrock | Claude による応答生成 |
| EventBridge | 定期実行サービスのスケジューリング |

## 開発スタンダード

### コード品質
- **Linter**: Ruff
- `F401` (未使用import)、`F841` (未使用変数) は自動修正しない

### 型安全性
- boto3-stubsで型補完を提供

### テスト方針
- **実機テスト重視**: 本番環境での動作確認
- 大規模なユニットテスト・CI/CDは構築しない

## 開発環境

### 必須ツール
- Python 3.14+
- uv
- AWS CDK CLI
- AWS CLI (認証設定済み)

### 共通コマンド
```bash
# 依存関係インストール
uv sync

# CDKデプロイ
cd libs/salome-cdk && cdk deploy

# ツール実行
uv run tools/xxx.py
```

## 重要な技術的決定

- **AWS SAM → CDK移行**: Lambda増加に伴う管理複雑化を解消
- **Strands Agents採用**: モダンなAIエージェントフレームワークで実装を簡素化
- **LiteLLM採用**: LLMプロバイダーの抽象化で将来の拡張性を確保
- **uvワークスペース**: libs内パッケージのローカル参照を可能に

---
_スタンダードとパターンを記載。全ての依存関係は列挙していません_
