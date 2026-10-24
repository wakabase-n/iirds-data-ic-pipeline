import argparse
import json
import logging
from pathlib import Path

from config import DEFAULT_SKOS_DICT_PATH
from modules.iirds_builder import build_iirds_base
from modules.jsonld_exporter import export_final_iirds_jsonld
from modules.skos_enricher import enrich_with_skos

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)

def run_pipeline(ndf_file: Path, skos_file: Path, output_file: Path, save_intermediates: bool):
    logging.info("=== Starting iiRDS Compiler Pipeline ===")
    
    with open(ndf_file, "r", encoding="utf-8") as f:
        ndf_facts = json.load(f)
    with open(skos_file, "r", encoding="utf-8") as f:
        skos_dict = json.load(f)

    iirds_base = build_iirds_base(ndf_facts)
    if save_intermediates:
        with open("step1_iirds_base.json", "w", encoding="utf-8") as f:
            json.dump(iirds_base, f, ensure_ascii=False, indent=2)

    enriched_data = enrich_with_skos(iirds_base, skos_dict)
    if save_intermediates:
        with open("step2_skos_enriched.json", "w", encoding="utf-8") as f:
            json.dump(enriched_data, f, ensure_ascii=False, indent=2)

    final_jsonld = export_final_iirds_jsonld(enriched_data)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(final_jsonld, f, ensure_ascii=False, indent=2)

    logging.info(f"=== Pipeline Finished! Output: {output_file} ===")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="iiRDS Compiler Pipeline CLI")
    parser.add_argument("--ndf", type=Path, default=Path("validated_facts.json"), help="Path to input NDF JSON file")
    parser.add_argument("--skos", type=Path, default=DEFAULT_SKOS_DICT_PATH, help="Path to SKOS dictionary JSON file")
    parser.add_argument("--output", "-o", type=Path, default=Path("iirds_data_ic.jsonld"), help="Path to output JSON-LD file")
    parser.add_argument("--no-intermediates", action="store_true", help="Disable saving intermediate JSON files")

    args = parser.parse_args()
    
    run_pipeline(
        ndf_file=args.ndf,
        skos_file=args.skos,
        output_file=args.output,
        save_intermediates=not args.no_intermediates
    )
    
