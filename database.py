from pymongo import MongoClient
from datetime import datetime
import json
import csv
import base64
import os
from typing import Dict, List, Optional
import logging
from dotenv import load_dotenv
import os

# Cấu hình logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
load_dotenv()  # tự động tìm và load file .env trong thư mục hiện tại
key = os.getenv("Link")

class Database:
    def __init__(self): # khởi tạo db
        try:
            self.client = MongoClient(key)
            self.db = self.client["database_label"]
            self.products_collection = self.db.products
            self.manufacturers_collection = self.db.manufacturers
            self.importers_collection = self.db.importers
            logger.info(f"Kết nối MongoDB thành công !" )
            self.create_indexes()
        except Exception as e:
            logger.error(f"Lỗi kết nối MongoDB: {e}")
            raise

    def create_indexes(self): # tạo index
        try:
            self.products_collection.create_index("image_name")
            self.products_collection.create_index("type")
            self.manufacturers_collection.create_index("company_name")
            self.importers_collection.create_index("company_name")
        except Exception as e:
            logger.error(f"Lỗi tạo indexes: {e}")

    def insert_product(self, data):
        if not data:
            return False
        try:
            # Lưu manufacturer
            manufacturer_id = self.manufacturers_collection.insert_one(
                data.get('manufacturer', {})
            ).inserted_id
            # Lưu importer
            importer_id = self.importers_collection.insert_one(
                data.get('importer', {})
            ).inserted_id # insert vào collection và lấy biến id của document thêm vào
            # Lưu product
            document = {
                "image_name": data.get('image_name', ''),
                "image_path": data.get('image_path', ''),
                "image_base64": data.get('image_base64', ''),
                "product_name": data.get('product_name', ''),
                "manufacturer_id": manufacturer_id,
                "importer_id": importer_id,
                "manufacturing_date": self.convert_date_format(data.get('manufacturing_date', '')),
                "expiry_date": self.convert_date_format(data.get('expiry_date', '')),
                "type": data.get('type', ''),
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
            self.products_collection.insert_one(document)
            return True
        except Exception as e:
            logger.error(f"Lỗi thêm sản phẩm: {e}")
            return False
    def insert_label(self,datas):
        sv_manufac = []
        sv_importer = []
        if not datas:
            return False
        try:
            for data in datas:
                sv_manufac.append(data.get('manufacturer', {}));
                sv_importer.append(data.get('importer', {}));
                
            manu_id = self.manufacturers_collection.insert_many(sv_manufac).insert_id
            import_id = self.importers_collection.insert_many(sv_importer).insert_id
            docs = []
            for j in range(len(sv_importer)):
                doc = {
                    "image_name": data.get('image_name', ''),
                    "image_path": data.get('image_path', ''),
                    "image_base64": data.get('image_base64', '') or self.image_to_base64(data.get('image_path', '')),
                    "product_name": data.get('product_name', ''),
                    "manufacturer_id": manu_id[j],
                    "importer_id": import_id[j],
                    "manufacturing_date": self.convert_date_format(data.get('manufacturing_date', '')),
                    "expiry_date": self.convert_date_format(data.get('expiry_date', '')),
                    "type": data.get('type', ''),
                    "created_at": datetime.now(),
                    "updated_at": datetime.now()
                    }
                docs.append(doc)
                db.products_collection.insert_many(docs)
                return True
        except Exception as e:
            logger.error(f"Lỗi thêm sản phẩm: {e}")
            return False
    def get_all_products(self) -> List[Dict]:
        try:
            pipeline = [
                {
                    "$lookup": {
                        "from": "manufacturers",
                        "localField": "manufacturer_id",
                        "foreignField": "_id",
                        "as": "manufacturer"
                    }
                },
                {"$unwind": {"path": "$manufacturer", "preserveNullAndEmptyArrays": True}},
                {
                    "$lookup": {
                        "from": "importers",
                        "localField": "importer_id",
                        "foreignField": "_id",
                        "as": "importer"
                    }
                },
                {"$unwind": {"path": "$importer", "preserveNullAndEmptyArrays": True}}, # chuyển 
                {
                    "$project": {
                        "_id": 0,
                        "image_name": 1,
                        "image_path": 1,
                        "image_base64": 1,
                        "product_name": 1,
                        "manufacturer": 1,
                        "importer": 1,
                        "manufacturing_date": 1,
                        "expiry_date": 1,
                        "type": 1
                    } # chỉ định những field sẽ được lấy 
                }
            ]
            return list(self.products_collection.aggregate(pipeline))
        except Exception as e:
            logger.error(f"Lỗi lấy danh sách sản phẩm: {e}")
            return []
def update_product(self, image_name, data) -> bool:
    try:
        # Tìm product theo image_name
        product = self.products_collection.find_one({"image_name": image_name})
        if not product:
            logger.warning(f"Không tìm thấy sản phẩm: {image_name}")
            return False
        
        # Cập nhật manufacturer nếu có
        if "manufacturer" in data:
            self.manufacturers_collection.update_one(
                {"_id": product["manufacturer_id"]},
                {"$set": data["manufacturer"]}
            )
        
        # Cập nhật importer nếu có
        if "importer" in data:
            self.importers_collection.update_one(
                {"_id": product["importer_id"]},
                {"$set": data["importer"]}
            )
        
        # Cập nhật product
        update_fields = {
            "product_name": data.get("product_name", product["product_name"]),
            "manufacturing_date": self.convert_date_format(data.get("manufacturing_date", "")),
            "expiry_date": self.convert_date_format(data.get("expiry_date", "")),
            "type": data.get("type", product["type"]),
            "updated_at": datetime.now()
        }
        
        self.products_collection.update_one(
            {"_id": product["_id"]},
            {"$set": update_fields}
        )

        logger.info(f"Cập nhật thành công sản phẩm: {image_name}")
        return True

    except Exception as e:
        logger.error(f"Lỗi cập nhật sản phẩm: {e}")
        return False

    def close_connection(self):
        self.client.close()
