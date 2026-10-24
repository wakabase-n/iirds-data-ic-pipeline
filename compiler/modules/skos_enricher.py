import json
import logging
from pathlib import Path

# ログ設定
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def enrich_with_skos(iirds_base: dict, skos_dict: dict) -> dict:
    logging.info("Starting SKOS concept and safety metadata enrichment...")
    
    symbols_map = skos_dict.get("symbols", {})
    keywords_map = skos_dict.get("keywords", {})
    
    # Pythonコード側で決定論的に処理する危険度判定辞書
    danger_rules = {
        "permanent electrical damage": "iirds:DANGER",
        "thermal damage": "iirds:WARNING",
        "logic failure": "iirds:CAUTION",
        "protection lock": "iirds:WARNING"
    }
    
    for node in iirds_base.get("@graph", []):
        node_type = node.get("@type")
        
        # 1. technical_data ノードへの SKOS URI 付与
        if node_type == "iirds:GenericTechnicalData":
            symbol = node.get("ise:symbol")
            if symbol in symbols_map:
                node["skos:exactMatch"] = symbols_map[symbol]
                logging.info(f"Bound SKOS URI to symbol '{symbol}': {symbols_map[symbol]}")
            else:
                logging.warning(f"Symbol '{symbol}' not found in skos_dictionary.")
                
        # 2. rules ノードへの SKOS URI および 危険度(dangerLevel) の自動割り当て
        elif node_type == "iirds:GenericConcept":
            keywords = node.get("ise:rawKeywords", [])
            matched_concepts = []
            assigned_danger = None
            
            for kw in keywords:
                # SKOS概念URIの割り当て
                if kw in keywords_map:
                    matched_concepts.append(keywords_map[kw])
                    logging.info(f"Bound SKOS concept for keyword '{kw}': {keywords_map[kw]}")
                
                # キーワードに基づく 100% 確定論的な dangerLevel の判定
                if kw in danger_rules and not assigned_danger:
                    assigned_danger = danger_rules[kw]
            
            if matched_concepts:
                node["skos:relatedConcept"] = matched_concepts
            
            if assigned_danger:
                node["iirds:dangerLevel"] = assigned_danger
                logging.info(f"Assigned dangerLevel '{assigned_danger}' for rule '{node.get('rdfs:label')}'")
                
    return iirds_base

if __name__ == "__main__":
    base_path = Path("step1_iirds_base.json")
    dict_path = Path("skos_dictionary.json")
    
    if not base_path.exists() or not dict_path.exists():
        logging.error("Input files (step1_iirds_base.json / skos_dictionary.json) missing!")
        exit(1)
        
    with open(base_path, "r", encoding="utf-8") as f:
        iirds_base = json.load(f)
        
    with open(dict_path, "r", encoding="utf-8") as f:
        skos_dict = json.load(f)
        
    # 変換実行
    enriched_data = enrich_with_skos(iirds_base, skos_dict)
    
    # 中間ファイル出力（Step 2 検証用）
    output_path = Path("step2_skos_enriched.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(enriched_data, f, ensure_ascii=False, indent=2)
        
    logging.info(f"Successfully exported Step 2 output to {output_path}")
    
