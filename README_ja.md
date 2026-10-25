
# Compiled Documentation: iirds-data-ic-pipeline
> 🌐 **Read this in other languages:** [English](README.md)

技術文書を「人が読むための静的なPDF」から、設計ツールやシミュレータを直接駆動させる「実行可能なデータ部品（Data IC）」へとコンパイルするためのデータ連携パイプラインです。

本リポジトリは、半導体マルチサプライヤー仕様検証を対象とした実証コード（MVP）を提供します。国際標準である **AAS (IDTA 02004)**、**iiRDS**、**W3C SKOS** を組み合わせ、自然言語の仕様書から100%型安全なナレッジグラフ（JSON-LD）を決定論的に生成します。

## 🌟 Core Architecture: AIの柔軟性と決定論の分離

大規模言語モデル（LLM）を用いた仕様書の直接変換は、確率的なハルシネーションや構文破壊（連動破壊）を引き起こすため、ゼロ・ディフェクトが求められるハードウェア設計には適用できません。

この問題を解決するため、本アーキテクチャでは処理を3つのフェーズに分離し、**「プロンプトによる厳格な中間フォーマット生成」**をシステムの要（防波堤）として配置しています。

1. **Phase 1: Fact Extraction (LLM)**
   高次解釈を禁止し、純粋なファクトと数式のみを抽出するスキーマ駆動型プロンプト。
2. **Phase 2: Quality Audit (LLM / HitL)**
   抽出されたデータに対する厳格な品質監査。100%の正確性を担保した上で次工程へ渡す。
3. **Phase 3: Deterministic Compiler (Python)**
   決定論的プログラムにより、SKOS概念をバインドし、型安全な iiRDS Data IC (JSON-LD) を生成する。

## 📁 Repository Structure

本リポジトリのディレクトリ構成は以下の通りです。

```text
├── compiler/                 # Phase 3: 決定論的コンパイラ
│   ├── mapping_rules/
│   │   └── skos_dictionary.json  # ベンダー固有語彙を共通URIへ変換する辞書
│   ├── modules/
│   │   ├── iirds_builder.py      # iiRDSグラフ構築モジュール
│   │   ├── jsonld_exporter.py    # JSON-LD出力モジュール
│   │   └── skos_enricher.py      # SKOS概念バインドモジュール
│   └── main.py               # コンパイラ実行のメインスクリプト
├── docs/
│   ├── images/                     # アーキテクチャ図および検証ベンチマーク画像アセット
│   ├── architecture.md             # システムアーキテクチャおよび段階的確定論的パイプライン仕様書 (EN)
│   ├── architecture_ja.md          # システムアーキテクチャ仕様書 (JA)
│   ├── intermediate_format.md      # 中間正規化JSONスキーマの設計原則と仕様定義 (EN)
│   ├── intermediate_format_ja.md   # 中間フォーマット仕様書 (JA)
│   └── verification_details.md     # Neo4j論理シミュレーション検証ベンチマークおよびCypherクエリ詳細 (検証1〜6)
├── neo4j/                    # 論理シミュレータ（Neo4j）用ディレクトリ
│   └── 検証用クエリ          # What-if分析・影響範囲特定用のCypherクエリスクリプト
├── projections/              # 生成された知識グラフからCAD/DRC用CSVへの切り出し処理と成果物
│   ├── combined_cad_rules.csv # DRCエンジン用の動的安全ルールデータ
│   └── combined_cad_specs.csv # ECADライブラリ用のピン・定格スペックデータ
├── prompts/                  # Phase 1 & 2: アーキテクチャの要となるプロンプト群
│   ├── 10_prompt_build_mid_file # 事実抽出・数式分離・サニタイズ用プロンプト
│   └── 20_prompt_audit_NDF       # データ品質監査・欠落検知用プロンプト
└── samples/                  # 実証用のサンプルデータセット
    ├── iirds_data_ic.jsonld  # 最終生成物（Data IC 知識グラフ）
    ├── input_datasheet       # 入力ソース（PDF/Markdown仕様書）
    └── normalized_facts.json # LLMによって抽出・正規化された中間フォーマット
````

## 🚀 Pipeline Execution Flow

### 1. ファクト抽出と中間フォーマットの生成 (`prompts/`)

`prompts/10_prompt_buildc_mid_file` を用いてLLMを実行し、入力仕様書（`samples/input_datasheet`）からファクトを抽出します。 LLMの自律的な推論を厳しく制限し、動的数式（例: `0.8 * VCC`）と静的数値を厳密に分離した `normalized_facts.json` を出力します。

### 2. データ品質の監査 (`prompts/20_prompt_audit_NDF`)

生成された中間フォーマットに対し、監査プロンプトを適用して原文との整合性をチェックします。ここで抽出漏れやルール違反がないことを保証し、後続のコンパイラを保護します。

### 3. 確定論的コンパイル (`compiler/main.py`)

Pythonコンパイラを実行し、検証済みの中間データから `samples/iirds_data_ic.jsonld` を構築します。 このプロセスは完全に決定論的であり、`mapping_rules/skos_dictionary.json` を参照して異ベンダー間の表記揺らぎを吸収します。

### 4. CAD/DRCへの多出力プロジェクション (`projections/`)

生成された単一のJSON-LDを走査し、EDAツール用のピン・定格スペック（CSV）や、DRCエンジン用の動的安全ルール（CSV）を手作業ゼロで切り出します。

### 5. Neo4jによる論理シミュレーション（ドキュメントのDRC）

`neo4j/検証用クエリ` を使用して、Neo4jグラフデータベース上で実行前検証を行います。 物理回路を組む前に、「特定パラメータ（VCC等）の変動がどの安全インターロックに波及するか」や「DANGERレベルのリスクパス」をミリ秒単位で特定します。

## 🤝 共同実証・フィードバックの募集

本アーキテクチャの社会実装・業界展開に向けて、共同検証（PoC）パートナーを募集しています。

* **デバイス・センサーベンダー様**: アプリケーションノートやデータシートのData IC化によるDesign-In高速化・FAE工数削減
* **セットメーカー・EDA/CAD関係者様**: 自社設計フロー（CAD/DRC）へのData IC取り込み・多出力プロジェクション接続検証
* **テクニカルコミュニケーター・標準化関係者様**: iiRDS / AAS / SKOS を活用した情報構造化の推進

共同検証のご相談やフィードバックは、Issue または下記連絡先までお気軽にお寄せください。

* **Author**: 若林 夏樹 (Natsuki Wakabayashi)
* **Organization**: 株式会社インフォメーション・システム・エンジニアリング
* **Role**: 
  * 情報アーキテクト（IA） / テクニカルコミュニケーター
  * IEC TC3 WG28 エキスパート
  * AEO（回答エンジン最適化）情報設計理論 推進者
* **Contact**: [LinkedInプロフィール](https://www.linkedin.com/in/natsuki-wakabayashi/)

 ## 📄 License & Citation

This repository and all its structural assets, prompts, and sample payloads are licensed under the **Creative Commons Attribution-NonCommercial 4.0 International License (CC BY-NC 4.0)**
- License: [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/)


### 🚀 Hands-on Sandbox Policy: Feel Free to Copy and Test!

We highly encourage readers, engineers, and researchers to freely copy, modify, and run these assets in your personal testing environments or local sandboxes. If these prompts and structured payloads help deepen your understanding of iiRDS and Answer Engine Optimization (AEO), this repository has fully achieved its purpose. Experimentation is the first step toward masterclass information architecture.

### ⚠️️ Strict Note for Commercial and Industrial Application
While personal testing and learning are entirely unrestricted, please note that these payloads are provided strictly as conceptual proof-of-concept (PoC) references built with deep respect for the official iiRDS (International Standard for Intelligent Information Request and Delivery) specifications managed by the tekom/iiRDS Consortium.

If your organization intends to deploy graph-aware atomic architectures or standardized metadata schemas in a commercial, production, or real-world industrial environment, you are strongly urged to:

1. **Consult the official primary sources**: Directly review the definitive specifications, official schemas, and validation toolkits at the [iiRDS Official Website](https://iirds.org/).
2. **Architect your own semantic model**: Do not blindly copy-paste these specific SP-X sample assets into production. Re-engineer and tailor your own knowledge graph frameworks based on the official guidelines to ensure true regulatory compliance, operational safety, and product liability (PL) defense. 
