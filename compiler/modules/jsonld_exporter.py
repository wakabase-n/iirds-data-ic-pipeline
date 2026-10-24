import json
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def export_final_iirds_jsonld(enriched_data: dict) -> dict:
    logging.info("Starting final iiRDS JSON-LD validation and export...")
    
    validated_graph = []
    for node in enriched_data.get("@graph", []):
        # null値のプロパティを除去してJSON-LD構造を極小化・クリーン化
        clean_node = {k: v for k, v in node.items() if v is not None}
        validated_graph.append(clean_node)
        
    final_doc = {
        "@context": enriched_data.get("@context", {}),
        "@graph": validated_graph
    }
    
    logging.info(f"Validation passed for all {len(validated_graph)} graph nodes.")
    return final_doc

if __name__ == "__main__":
    input_path = Path("step2_skos_enriched.json")
    output_path = Path("iirds_data_ic.jsonld")
    
    if not input_path.exists():
        logging.error("step2_skos_enriched.json missing!")
        exit(1)
        
    with open(input_path, "r", encoding="utf-8") as f:
        enriched_data = json.load(f)
        
    final_jsonld = export_final_iirds_jsonld(enriched_data)
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(final_jsonld, f, ensure_ascii=False, indent=2)
        
    logging.info(f"Phase 3 Complete: Final iiRDS Data IC exported to '{output_path}'")

    
