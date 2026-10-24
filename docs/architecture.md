# Pipeline Architecture: The Stepwise Deterministic Approach

The core of this architecture lies in completely separating the responsibilities of probabilistic "AI flexibility" and the strict "program determinism" (100% type safety) required for hardware design. To prevent hallucinations and syntax corruption caused by direct LLM conversion, the processing pipeline is divided into three distinct phases and one critical intermediate format.

## System Flow

```text
 [ Unstructured Specifications from Multiple Vendors (PDF / Markdown / HTML) ]
 │
 ▼
【 Phase 1: LLM (Parsing & Normalization Engine) 】
 │ ・ Completely prohibits the LLM from interpreting complex iiRDS or SKOS ontologies.
 │ ・ Strictly focuses on extracting "objective facts and mathematical formulas" from text.
 │
 ▼
[ Intermediate Format (Simple Normalized JSON) ]
 │ ・ Features flat pin lists, strict separation of numbers/formulas, and sanitized plain text.
 │ ・ Acts as a "type-safe breakwater" bridging AI extraction and deterministic programming.
 │
 ▼
【 Phase 2: Python (Data Quality Audit & HitL) 】
 │ ・ Executes numeric type checks and mandatory key completeness checks based on a JSON Schema.
 │ ・ Isolates rule violations or uncertain extracted data for Human-in-the-Loop (HitL) review.
 │
 ▼
【 Phase 3: Python (Deterministic iiRDS / SKOS Compiler) 】
 │ ・ Refers to an external dictionary (skos_dictionary.json) to map vendor dialects to standard URIs.
 │ ・ Builds the graph structure by assigning classes and properties using 100% deterministic logic.
 │
 ▼
[ 100% Type-Safe iiRDS Data IC (JSON-LD) ]
````

## Architectural Benefits

- **Blocking Hallucinations**: By stripping the LLM of ontology knowledge and hazard-level deduction, and delegating these tasks to deterministic Python code downstream (Phase 3), we ensure that no AI-induced probabilistic variations or hallucinations contaminate the final output.
    
- **Enhanced Maintainability**: The pipeline features a loosely coupled design. Vendor-specific formatting differences are absorbed by the prompt in Phase 1, while updates to international standards or output schemas are handled independently by the Python compiler in Phase 3.