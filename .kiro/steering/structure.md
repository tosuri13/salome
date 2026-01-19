# プロジェクト構造

## 組織哲学

**モノレポ・ワークスペースパターン**を採用。Discord Bot機能とAWSインフラを分離しつつ、単一リポジトリで管理。

## ディレクトリパターン

### アプリケーション層
**場所**: `/apps/`
**目的**: デプロイ可能なLambda関数群

#### functions/api
**場所**: `/apps/functions/api/`
**目的**: Discord Webhookを受け付けるAPIエンドポイント
**例**: 署名検証、コマンドルーティング

#### functions/server
**場所**: `/apps/functions/server/`
**目的**: 各Slash Commandの処理Lambda
**例**: `ask.py`, `recipe.py`, `minecraft.py`, `garbage.py`

### 共有ライブラリ層
**場所**: `/libs/`
**目的**: 再利用可能なPythonパッケージ

#### salome (コアライブラリ)
**場所**: `/libs/salome/`
**目的**: AIエージェント機能、ツール、ユーティリティ
**構造**:
- `src/salome/agents/` - Strands Agentsベースのエージェント実装
- `src/salome/tools/` - エージェント用ツール（Minecraft操作、レシピ検索など）
- `src/salome/utils/` - 共通ユーティリティ
  - `utils/aws/` - boto3ラッパー、Bedrock連携
  - `utils/discord/` - Discord API操作

#### salome-cdk (インフラ)
**場所**: `/libs/salome-cdk/`
**目的**: AWS CDKスタック定義
**構造**:
- `app.py` - CDKアプリエントリポイント
- `stacks/` - CDKスタック定義
  - API Gateway + Lambda (Router)
  - SNS Topics
  - Lambda Functions (Handlers)
  - EventBridge Rules (定期実行)

### ツール
**場所**: `/tools/` (予定)
**目的**: Discord Botへのコマンド登録などの運用ツール

## 命名規則

- **ファイル**: snake_case（例: `ask_handler.py`）
- **クラス**: PascalCase（例: `AskAgent`）
- **関数/変数**: snake_case（例: `handle_command`）
- **Lambdaハンドラ**: `handler` 関数をエクスポート
- **パッケージ**: kebab-case（例: `salome-cdk`）

## インポート規則

```python
# 標準ライブラリ
import os
from typing import Any

# サードパーティ
import boto3
from strands import Agent

# ローカルパッケージ
from salome.agents import LadyClaudeAgent
from salome.utils.discord import send_followup_message
```

## コード組織の原則

- 各Slash Commandは独立したLambda関数として実装
- 共通ロジック（Discord連携、Bedrock呼び出し）は`salome`パッケージに集約
- インフラコード（CDK）はアプリケーションコードと分離
- 1つのスタックで全リソースを管理（個人プロジェクトのためシンプルに）

---
_パターンを記載。ディレクトリツリー全体は列挙していません。パターンに従う新規ファイルは更新不要_
