from pymongo import MongoClient
from datetime import datetime
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
            print("Collections:", self.client["database_label"].list_collection_names())
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
            self.products_collection.create_index("image_name",unique=True, background=True)
            self.products_collection.create_index("importer_id",background=True)
            self.products_collection.create_index("manufacturer_id",background=True)
        except Exception as e:
            logger.error(f"Lỗi tạo indexes: {e}")

    def insert_label(self,datas):
        sv_manufac = []
        sv_importer = []
        if not datas:
            return False
        try:
            for data in datas:
                sv_manufac.append(data.get('manufacturer', {}))
                sv_importer.append(data.get('importer', {}))
                
            manu_id = self.manufacturers_collection.insert_many(sv_manufac).inserted_ids
            import_id = self.importers_collection.insert_many(sv_importer).inserted_ids
            docs = []
            for j in range(len(sv_importer)):
                doc = {
                    "image_name": datas[j].get('image_name', ''),
                    "image_bas64": datas[j].get('image_base64',''),
                    "image_path": datas[j].get('image_path', ''),
                    "image_base64": datas[j].get('image_base64', '') ,
                    "product_name": datas[j].get('product_name', ''),
                    "manufacturer_id": manu_id[j],
                    "importer_id": import_id[j],
                    "manufacturing_date": datas[j].get('manufacturing_date', ''),
                    "expiry_date": datas[j].get('expiry_date', ''),
                    "type": datas[j].get('type', ''),
                    "created_at": datetime.now(),
                    "updated_at": datetime.now()
                    }
                docs.append(doc)
            self.products_collection.insert_many(docs,ordered=False)
            return True
        except Exception as e:
            logger.error(f"Lỗi thêm sản phẩm: {e}")
            return False
    def get_product(self, name_image):
        try:
            pipeline = [
                {"$match": {"image_name": name_image}},
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
                {"$unwind": {"path": "$importer", "preserveNullAndEmptyArrays": True}},
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
                    }
                }
            ]
            result = list(self.products_collection.aggregate(pipeline))
            
            if result:
                return result[0]
            else:
                print(f"Sản phẩm chưa có dữ liệu: {name_image}")
                return {}
        except Exception as e:
            logger.error(f"Lỗi lấy danh sách sản phẩm: {e}")
            return {}
        
    def get_all_products(self):  # trả về list[dict]
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
                        "manufacturer": {
                            "name": "$manufacturer.name_xuat",
                            "address": "$manufacturer.address_xuat",
                            "phone": "$manufacturer.sdt_xuat"
                            },
                        "importer": {
                            "name": "$importer.name_nhap",
                            "address": "$importer.address_nhap",
                            "phone": "$importer.sdt_nhap"
                        },
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
    def update_product(self, image_name, data):
        try:
            # Tìm product theo image_name
            product = self.products_collection.find_one({"image_name": image_name})
            if not product:
                logger.warning(f"Không tìm thấy sản phẩm: {image_name}")
                return False
            
            # Cập nhật manufacturer nếu có
            if "manufacturer" in data:
                tmp = self.manufacturers_collection.find_one({"_id": product["manufacturer_id"]}, {"_id": 0})
                if tmp != data["manufacturer"]:
                    self.manufacturers_collection.update_one(
                        {"_id": product["manufacturer_id"]},
                        {"$set": data["manufacturer"]}
                    )
            
            # Cập nhật importer nếu có
            if "importer" in data:
                tmp = self.importers_collection.find_one({"_id": product["importer_id"]},{"_id": 0})
                if tmp != data["importer"]:
                    self.importers_collection.update_one(
                        {"_id": product["importer_id"]},
                        {"$set": data["importer"]}
                    )
            
            # Cập nhật product
            update_fields = {
                "product_name": data.get("product_name", product["product_name"]),
                "manufacturing_date": data.get("manufacturing_date", product["manufacturing_date"]),
                "expiry_date": data.get("expiry_date", product["expiry_date"]),
                "type": data.get("type", product["type"]),
                "updated_at": datetime.now()
            }
            
            if any(update_fields[k] != product.get(k) for k in update_fields):
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
