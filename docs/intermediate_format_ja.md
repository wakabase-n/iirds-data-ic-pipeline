
# Intermediate Format (Simple Normalized JSON) Specification

中間フォーマット（Simple Normalized JSON）の目的は、「LLMが抽出時にアテンションを分散させず、後続のPythonプログラムが100%決定論的なロジックで型チェックおよび規格バインド（iiRDS化）を実行できる構造」を提供することです。

## 中間フォーマット設計の4大原則

1. **高次セマンティクスの完全排除（ファクト特化）**
   `iirds:GenericConcept` や SKOS URI、危険度判定（`danger_level`）といった規格解釈の責務をLLMに持たせません。ドキュメントに記載された「客観的事実（ファクト）」のみをフラットな構造で抽出させます。

2. **値（Value）と数式（Formula）の厳格なキー分離**
   型の判定曖昧さを排除するため、純粋な数値（`float`）を格納するキー（`numeric_values`）と、変数を含む文字列式（例: `0.8 * VCC`）を格納するキー（`formula_values`）をスキーマレベルで厳格に分離します。これにより、プログラム側でのパースエラーを防止します。

3. **サニタイズ済みの文字列保持（ノイズ排除）**
   Markdownの装飾記号（`###`, `*`, `_` など）は、Phase 1（LLM抽出）の時点でプレーンテキストへサニタイズさせます。後続のPythonスクリプトにおける文字列処理コストや誤判定リスクをゼロにします。

4. **原文追跡性（トレーサビリティ）の確保**
   Phase 2の品質監査（Human-in-the-Loop）において修正や検証を容易にするため、原文の節見出し（`section_title`）や原文テキスト（`raw_text`）をそのままの形で保持します。

## 期待されるJSONスキーマ実装例 (`normalized_facts.json`)

```json
{
  "product_identification": "ISE-NAND01G-3V3",
  "components": [
    {
      "id": "B-01",
      "name": "VCC",
      "category": "Power",
      "description": "Core Power Supply (3.3V)"
    }
  ],
  "technical_data": [
    {
      "parameter": "High Level Input Voltage",
      "symbol": "VIH",
      "unit": "V",
      "numeric_values": {
        "min": null,
        "typ": null,
        "max": null
      },
      "formula_values": {
        "min_formula": "0.8 * VCC",
        "max_formula": "VCC + 0.3"
      },
      "test_condition": null
    },
    {
      "parameter": "Low Level Input Voltage",
      "symbol": "VIL",
      "unit": "V",
      "numeric_values": {
        "min": -0.3,
        "typ": null,
        "max": null
      },
      "formula_values": {
        "min_formula": null,
        "max_formula": "0.2 * VCC"
      },
      "test_condition": null
    }
  ],
  "statements_and_rules": [
    {
      "rule_id": "Rule #102",
      "section_title": "3.2 Interlock and Safety Exceptions",
      "raw_text": "When Error Code E-404 (Over-current / Motor Overload Signal) is asserted by the host system, AUX_PWR must remain supplied at 5.0V for at least 30 seconds to complete the internal safe-discharge sequence. Opening the module cover or cutting AUX_PWR before 30 seconds have elapsed may cause permanent electrical damage to the microbump array.",
      "fact_elements": {
        "trigger_signal": "Error Code E-404",
        "target_component": "AUX_PWR",
        "required_value": "5.0V",
        "duration": ">= 30 seconds"
      },
      "text_keywords": [
        "permanent electrical damage",
        "safe-discharge"
      ]
    }
  ]
}
````

## コンパイラ（Phase 3）における決定論的処理の実現

この中間フォーマットを入力とすることで、Pythonコンパイラは以下の処理をバグや推論ミスなく100%決定論的に実行します。
- **`topic_type`の判定**: `technical_data` ブロックの要素には無条件で `iirds:GenericTechnicalData` を付与し、`statements_and_rules` に `trigger_signal` 等が含まれる場合は `iirds:GenericConcept` を付与します。
- **`danger_level`の判定**: `text_keywords` や `raw_text` に含まれるフレーズ（例: "permanent damage" -> `DANGER`）を、Python側の静的辞書で評価し割り当てます。LLMの気分に依存しません。
- **`ise:formula`の構築**: `formula_values` に文字列が存在する場合のみ、数式オブジェクトとして安全に構築します。