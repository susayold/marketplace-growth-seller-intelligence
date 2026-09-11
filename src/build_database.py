"""Build and load the PostgreSQL raw-to-fact layer from Drive-materialized ZIPs.

Raw archives remain outside GitHub. The command reads them from OLIST_RAW_DIR,
creates the governed schemas, COPY-loads raw tables, then builds staging,
dimensions, facts, marts and quality objects in dependency order.
"""
from __future__ import annotations
import argparse
import logging
import os
from pathlib import Path
from zipfile import ZipFile
import pandas as pd
try:
    from .utils.db import connect, copy_dataframe, run_sql_files
    from .utils.io import read_zip_csv
    from .utils.logging import configure_logging
except ImportError:
    from utils.db import connect, copy_dataframe, run_sql_files
    from utils.io import read_zip_csv
    from utils.logging import configure_logging


SOURCE_SPECS = [
    ("brazilian-ecommerce.zip", "olist_orders_dataset.csv", "raw.olist_orders", ["order_id", "customer_id", "order_status", "order_purchase_timestamp", "order_approved_at", "order_delivered_carrier_date", "order_delivered_customer_date", "order_estimated_delivery_date"]),
    ("brazilian-ecommerce.zip", "olist_order_items_dataset.csv", "raw.olist_order_items", ["order_id", "order_item_id", "product_id", "seller_id", "shipping_limit_date", "price", "freight_value"]),
    ("brazilian-ecommerce.zip", "olist_order_payments_dataset.csv", "raw.olist_order_payments", ["order_id", "payment_sequential", "payment_type", "payment_installments", "payment_value"]),
    ("brazilian-ecommerce.zip", "olist_order_reviews_dataset.csv", "raw.olist_order_reviews", ["review_id", "order_id", "review_score", "review_creation_date", "review_answer_timestamp"]),
    ("brazilian-ecommerce.zip", "olist_customers_dataset.csv", "raw.olist_customers", ["customer_id", "customer_unique_id", "customer_zip_code_prefix", "customer_city", "customer_state"]),
    ("brazilian-ecommerce.zip", "olist_sellers_dataset.csv", "raw.olist_sellers", ["seller_id", "seller_zip_code_prefix", "seller_city", "seller_state"]),
    ("brazilian-ecommerce.zip", "olist_products_dataset.csv", "raw.olist_products", ["product_id", "product_category_name", "product_name_lenght", "product_description_lenght", "product_photos_qty", "product_weight_g", "product_length_cm", "product_height_cm", "product_width_cm"]),
    ("brazilian-ecommerce.zip", "olist_geolocation_dataset.csv", "raw.olist_geolocation", ["geolocation_zip_code_prefix", "geolocation_lat", "geolocation_lng", "geolocation_city", "geolocation_state"]),
    ("marketing-funnel-olist.zip", "olist_marketing_qualified_leads_dataset.csv", "raw.mql", ["mql_id", "first_contact_date", "landing_page_id", "origin"]),
    ("marketing-funnel-olist.zip", "olist_closed_deals_dataset.csv", "raw.closed_deals", ["mql_id", "seller_id", "sdr_id", "sr_id", "won_date", "business_segment", "lead_type", "lead_behaviour_profile", "has_company", "has_gtin", "average_stock", "business_type", "declared_product_catalog_size", "declared_monthly_revenue"]),
]


def actual_member(zip_path: Path, filename: str) -> str:
    with ZipFile(zip_path) as zf:
        names = {Path(name).name: name for name in zf.namelist()}
    if filename not in names:
        raise FileNotFoundError(f"{filename} not found in {zip_path.name}")
    return names[filename]


def load_raw(raw_dir: Path, logger: logging.Logger) -> int:
    total = 0
    with connect() as conn:
        for archive, filename, table, columns in SOURCE_SPECS:
            archive_path = raw_dir / archive
            frame = read_zip_csv(archive_path, actual_member(archive_path, filename))
            rows = copy_dataframe(conn, table, frame, columns)
            total += rows
            logger.info("input file=%s rows read=%s rows loaded=%s", filename, len(frame), rows)
        conn.commit()
    return total


def model_files(project: Path) -> list[Path]:
    paths = [project / "sql/00_admin/00_schemas.sql"]
    paths += sorted((project / "sql/01_raw").glob("*.sql"))
    for folder in ("02_staging", "03_dimensions", "04_facts", "05_marts", "06_quality", "07_analysis"):
        paths += sorted((project / "sql" / folder).glob("*.sql"))
    return paths


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-dir", default=".")
    parser.add_argument("--raw-dir", default=os.getenv("OLIST_RAW_DIR", "data/raw"))
    parser.add_argument("--schema-only", action="store_true", help="create model objects without loading raw ZIPs")
    args = parser.parse_args()
    project, raw_dir = Path(args.project_dir), Path(args.raw_dir)
    logger = configure_logging(project / "reports/qa/pipeline_run.log")
    run_sql_files(model_files(project)[:2])
    loaded = 0
    if not args.schema_only:
        if not (raw_dir / "brazilian-ecommerce.zip").exists() or not (raw_dir / "marketing-funnel-olist.zip").exists():
            raise FileNotFoundError("Both raw ZIPs are required unless --schema-only is used")
        loaded = load_raw(raw_dir, logger)
    run_sql_files(model_files(project)[2:])
    logger.info("rows loaded=%s model files executed=%s warnings=%s errors=%s", loaded, len(model_files(project)), 0, 0)
    print(f"loaded_rows={loaded} sql_files={len(model_files(project))}")


if __name__ == "__main__":
    main()

