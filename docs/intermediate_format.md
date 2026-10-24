# Intermediate Format (Simple Normalized JSON) Specification

The primary objective of the Intermediate Format (Simple Normalized JSON) is to provide a structure that prevents LLM attention drift during extraction, while enabling the downstream Python program to execute 100% deterministic type-checking and ontology binding (iiRDS compilation).

## Four Core Principles of Intermediate Format Design

1. **Complete Elimination of High-Level Semantics (Fact-Centric)**
   The LLM is strictly prohibited from interpreting standards, such as assigning `iirds:GenericConcept`, SKOS URIs, or determining hazard severities (`danger_level`). It is constrained to extract only the "objective facts" stated in the document into a flat structure.

2. **Strict Key Separation of Values and Formulas**
   To eliminate type ambiguity, the schema strictly separates pure numeric values (`float`) stored in keys like `numeric_values` from strings containing variables and equations (e.g., `0.8 * VCC`) stored in `formula_values`. This structural isolation prevents parsing errors in the downstream compiler.

3. **Retention of Sanitized Strings (Noise Elimination)**
   Markdown decoration symbols (e.g., `###`, `*`, `_`) must be sanitized into plain text at the point of LLM extraction (Phase 1). This reduces string processing overhead and eliminates the risk of misinterpretation in subsequent Python scripts.

4. **Ensuring Traceability**
   To facilitate easy verification and manual correction during the Quality Audit phase (Human-in-the-Loop), the original section headers (`section_title`) and the verbatim original text (`raw_text`) are preserved identically within the schema.

## Expected JSON Schema Implementation (`normalized_facts.json`)

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

## Realizing Deterministic Processing in the Compiler (Phase 3)

By using this intermediate format as input, the Python compiler can execute the following processes 100% deterministically, with zero room for bugs or AI hallucinations:

- **Determining `topic_type`**: Elements within the `technical_data` block unconditionally receive `iirds:GenericTechnicalData`. If `statements_and_rules` contain triggers like `trigger_signal`, they are assigned `iirds:GenericConcept`.
    
- **Determining `danger_level`**: Phrases found in `text_keywords` or `raw_text` (e.g., "permanent damage" -> `DANGER`) are evaluated and assigned by a static dictionary on the Python side, completely independent of the LLM's probabilistic mood.
    
- **Constructing `ise:formula`**: The system safely constructs algebraic formula objects if and only if strings are present within the `formula_values` object.