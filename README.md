
# iiRDS Data IC Pipeline
**AAS / iiRDS / SKOS を活用した半導体仕様ナレッジグラフの確定論的自動生成パイプライン**

本リポジトリは、半導体・電子部品の技術仕様書（自然言語・PDF）から、設計ツールやシミュレータが直接解釈可能な「実行可能な情報部品（Data IC: JSON-LD）」を確定論的に生成・検証するパイプラインの実証コードおよび検証データセットを管理するプロジェクトです。

---

## 📢 お知らせ（Status: Coming Soon）

本プロジェクトは **TCシンポジウム2026（2026年10月）** における発表内容と連動しています。  
現在、発表で提示した各実験データ・コードの整理およびドキュメンテーションを進めており、**2026年10月中旬〜下旬にかけて順次コードおよび検証資産を公開予定**です。

STARまたはWatchを登録してお待ちいただけますと幸いです。

---

## 💡 プロジェクト概要

半導体サプライチェーンにおいて、CADデータ（形状・接続）とPDF仕様書（動的安全制約・定格）の「データの断絶」は、手動入力による工数浪費や試作後の破壊事故を招く要因となっています。

本パイプラインは、生成AIの文脈理解力（確率論）とプログラムの検証力（確定論）を「中間フォーマット（Normalized Datasheet Format: NDF）」で物理絶縁し、以下の3大価値を実現します。

1. **ハルシネーションの絶縁**: LLMに規格文法を背負わせず客観ファクト抽出に特化させ、型安全性を100%保証
2. **手作業ゼロの多出力プロジェクション**: 単一のData ICからECAD用スペックCSVおよびDRC用ルールCSVを自動切り出し
3. **回路設計前の論理シミュレーション**: Neo4jナレッジグラフ上で、What-if影響分析や安全例外規定（DANGER）の自動診断を実行

---

## 🛠 パイプライン構造

```text
[ 仕様書 (PDF/MD/HTML) ]
       │
       ▼
【 Phase 1: LLM (パース・正規化エンジン) 】
   ・規格知識を追わせず、3大アンカーの客観ファクト抽出とサニタイズ
       │
       ▼
[ 中間フォーマット (normalized_facts.json) ]
       │
       ▼
【 Phase 2: Python (自動監査・型バリデータ & HitL) 】
   ・数値型チェック、動的数式のキー分離チェック、低信頼度項目の隔離
       │
       ▼
[ 検証済み中間データ (validated_facts.json) ]
       │
       ▼
【 Phase 3: Python (iiRDS / SKOS 確定コンパイラ) 】
   ・外部SKOS辞書を参照し、RDF骨格構築と概念URIバインドを一括実行
       │
       ▼
[ iiRDS Data IC (iirds_data_ic.jsonld) ]
       ├─► [ CAD用スペックCSV (combined_cad_specs.csv) ]
       ├─► [ DRC用ルールCSV (combined_cad_rules.csv) ]
       └─► [ Neo4j ナレッジグラフ (論理シミュレータ) ]
````

## 📁 公開予定のアーティファクト構成

順次、以下の資産を本リポジトリにコミット・公開します。

Plaintext

```
iirds-data-ic-pipeline/
├── README.md
├── docs/                      # アーキテクチャ解説・仕様ドラフト
│   ├── intermediate_format.md # 中間フォーマット（NDF）仕様定義
│   └── architecture.md        # パイプライン設計書
├── samples/                   # 検証用サンプルデータ
│   ├── input_datasheet.md     # サンプル仕様書（ISE-NAND01G-3V3）
│   ├── normalized_facts.json  # Phase 1 出力（中間データ）
│   └── iirds_data_ic.jsonld   # Phase 3 出力（完成Data IC）
├── compiler/                  # Python 確定論的コンパイラ本体
│   ├── main.py
│   ├── modules/
│   │   ├── iirds_builder.py   # iiRDS RDF骨格生成
│   │   ├── skos_enricher.py   # SKOS概念URIバインド
│   │   └── jsonld_exporter.py # 検証・JSON-LD出力
│   └── mapping_rules/
│       └── skos_dictionary.json
├── projections/               # 多出力プロジェクション（CSV切り出し）
└── neo4j/                     # 検証用Cypherクエリ一式
    ├── 01_import.cypher
    ├── 02_impact_analysis.cypher
    └── 03_safety_audit.cypher
```

## 🤝 共同実証・フィードバックの募集

本アーキテクチャの社会実装・業界展開に向けて、共同検証（PoC）パートナーを募集しています。

- **デバイス・センサーベンダー様**: アプリケーションノートやデータシートのData IC化によるDesign-In高速化・FAE工数削減
    
- **セットメーカー・EDA/CAD関係者様**: 自社設計フロー（CAD/DRC）へのData IC取り込み・多出力プロジェクション接続検証
    
- **テクニカルコミュニケーター・標準化関係者様**: iiRDS / AAS / SKOS を活用した情報構造化の推進
    

共同検証のご相談やフィードバックは、Issue または下記連絡先までお気軽にお寄せください。

- **Author**: 若林 夏樹 (Natsuki Wakabayashi)
- **Organization**: 株式会社情報システムエンジニアリング
- **Role**: IEC TC3 WG28 エキスパート 
- **Contact**: [LinkedIn]https://www.linkedin.com/in/natsuki-wakabayashi/

## 📄 License & Citation

This repository and all its structural assets, prompts, and sample payloads are licensed under the **Creative Commons Attribution-NonCommercial 4.0 International License (CC BY-NC 4.0)**.

- License: [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/)
    

### 🚀 Hands-on Sandbox Policy: Feel Free to Copy and Test!

We highly encourage readers, engineers, and researchers to freely copy, modify, and run these assets in your personal testing environments or local sandboxes. If these prompts and structured payloads help deepen your understanding of iiRDS and Answer Engine Optimization (AEO), this repository has fully achieved its purpose. Experimentation is the first step toward masterclass information architecture.

### ⚠️️ Strict Note for Commercial and Industrial Application

While personal testing and learning are entirely unrestricted, please note that these payloads are provided strictly as conceptual proof-of-concept (PoC) references built with deep respect for the official iiRDS (International Standard for Intelligent Information Request and Delivery) specifications managed by the tekom/iiRDS Consortium.

If your organization intends to deploy graph-aware atomic architectures or standardized metadata schemas in a commercial, production, or real-world industrial environment, you are strongly urged to:

1. **Consult the official primary sources**: Directly review the definitive specifications, official schemas, and validation toolkits at the [iiRDS Official Website](https://www.google.com/search?q=https://iirds.org/).
    
2. **Architect your own semantic model**: Do not blindly copy-paste these specific SP-X sample assets into production. Re-engineer and tailor your own knowledge graph frameworks based on the official guidelines to ensure true regulatory compliance, operational safety, and product liability (PL) defense.
