import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from config import IIRDS_CONTEXT

# ログ設定
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def build_iirds_base(ndf_data: dict) -> dict:
    logging.info("Starting iiRDS base graph construction...")

    product_id = ndf_data.get("product_identification", "Unknown")

    current_timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    
    iirds_doc = {"@context": IIRDS_CONTEXT, "@graph": []}
    
    # 1. Product (Component / Device) ノード
    product_node = {
        "@id": f"urn:product:{product_id.replace(' ', '_')}",
        "@type": "iirds:Component",
        "rdfs:label": product_id,
        "dcterms:created": current_timestamp
    }
    iirds_doc["@graph"].append(product_node)
    
    # 2. technical_data の変換 (iirds:GenericTechnicalData)
    for tech in ndf_data.get("technical_data", []):
        tech_node = {
            "@id": f"urn:techdata:{tech.get('symbol')}",
            "@type": "iirds:GenericTechnicalData",
            "rdfs:label": tech.get("parameter"),
            "ise:symbol": tech.get("symbol"),
            "ise:unit": tech.get("unit"),
            "ise:values": tech.get("numeric_values")
        }
        
        # 動的数式が存在する場合の決定論的バインド
        if tech.get("formula_values", {}).get("min_formula") or tech.get("formula_values", {}).get("max_formula"):
            tech_node["ise:formula"] = tech.get("formula_values")
            
        iirds_doc["@graph"].append(tech_node)
        logging.info(f"Built technical_data node: {tech.get('symbol')}")
        
    # 3. statements_and_rules の変換 (iirds:GenericConcept)
    for rule in ndf_data.get("statements_and_rules", []):
        rule_node = {
            "@id": f"urn:rule:{rule.get('rule_id').replace(' ', '_')}",
            "@type": "iirds:GenericConcept",
            "rdfs:label": rule.get("section_title"),
            "iirds:hasText": rule.get("raw_text"),
            "ise:factElements": rule.get("fact_elements"),
            "ise:rawKeywords": rule.get("text_keywords")
        }
        iirds_doc["@graph"].append(rule_node)
        logging.info(f"Built rule node: {rule.get('rule_id')}")

    return iirds_doc

if __name__ == "__main__":
    # NDFファイルの読み込み
    ndf_path = Path("validated_facts.json")
    if not ndf_path.exists():
        logging.error("validated_facts.json not found!")
        exit(1)
        
    with open(ndf_path, "r", encoding="utf-8") as f:
        ndf_facts = json.load(f)
        
    # 変換実行
    iirds_base = build_iirds_base(ndf_facts)
    
    # 中間ファイル出力（開発・目視確認用）
    output_path = Path("step1_iirds_base.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(iirds_base, f, ensure_ascii=False, indent=2)
        
    logging.info(f"Successfully exported Step 1 output to {output_path}")

