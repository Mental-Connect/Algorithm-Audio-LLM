from numpy import pad
from pymongo import MongoClient
from Service.common.constants import mongo_connect_str,default_db,secret_key
from base64 import b64decode, b64encode
from Crypto.Cipher import Blowfish


class DatabaseManager():
    school_user_collection_prefix = "school_user_"
    account_collection = "account"
    appointment_collection = "appointment"
    def __init__(self) -> None:
        self.client = MongoClient(mongo_connect_str)  # 初始化连接
        self.db = self.__get_db()  # 初始化默认数据库
    
    # 根据姓名查询学生
    # name 学生姓名
    def get_school_user(self, name:str) -> list:
        user_collection_names = self.get_user_collection_names()
        result = []
        for collection_name in user_collection_names:
            collection = self.db[collection_name]
            result.append(collection.find({"name": name}))
        return result
    
    # 根据姓名和所在学校查询学生
    # name 学生姓名
    def get_school_user(self, name:str, school_id:str) -> list:
        collection_name = f"{self.school_user_collection_prefix}{school_id}"
        collection = self.db[collection_name]
        return list(collection.find({"name": name},{"testingInfos": 0}))
         
    
    # 根据姓名,所在学校,所在班级查询学生
    def get_school_user(self, name:str, school_id:str, class_id) -> list:
        collection_name = f"{self.school_user_collection_prefix}{school_id}"
        collection = self.db[collection_name]
        return collection.find({"name": name,"org":class_id})
            
    # 根据id查询管理员
    def get_account_identity(self, id:str):
        collection = self.db[self.account_collection]
        return collection.find_one({"_id":id})
        
    # 获取所有学校中包含的所有姓名
    # 返回一个字典,字典中包含所有的学校和其中所有学生姓名,进行了去重
    def get_student_names(self) -> {str,list[str]}:
        results = {}
        user_name_parameter = "name"
        user_collection_names = self.get_user_collection_names()
        for collection_name in user_collection_names:
            collection = self.db[collection_name]
            school_id = collection_name.replace(self.school_user_collection_prefix, "")
            user_names = collection.find({},{"_id":0, user_name_parameter:1})
            results[school_id] = list({doc[user_name_parameter] for doc in user_names if user_name_parameter in doc})
        return results
    
    # 获取所有school_user表
    def get_user_collection_names(self):
        collection_names = self.db.list_collection_names()
        return [self.__decrypt_data(name) for name in collection_names if name.startswith(self.school_user_collection_prefix)]

    # 获取学生的最新的已完成访谈数据
    def get_student_appointment(self, user_id) ->dict:
        collection = self.db[self.appointment_collection]
        interview = collection.find_one({"schoolUserId": user_id, "status":"Scheduled"}, sort=[("timeStamp", -1)])
        return dict(interview) if interview else None
    
    def get_student_interviews(self, user_id) -> dict:
        collection = self.db[self.appointment_collection]
        interview = collection.find_one({"schoolUserId": user_id, "status":"Completed"}, sort=[("timeStamp", -1)])
        return dict(interview) if interview else None
    
    # 获取指定数据库名的数据库对象
    # db_name 数据库名
    def __get_db(self, db_name = default_db):
        db = self.client[db_name]
        return db
    
    def __decrypt_data(encryption_data_base64:str) -> str:
        # 解码 key 和密文
        key_bytes = b64decode(secret_key)
        encrypted_data = b64decode(encryption_data_base64)

        # 创建 Blowfish 解密器
        cipher = Blowfish.new(key_bytes, Blowfish.MODE_ECB)

        # 解密数据
        decrypted_data = cipher.decrypt(encrypted_data)

        # Blowfish 是 block cipher，解密结果可能包含填充，需要手动去除
        # 常见是 PKCS5/PKCS7 填充 —— 去除尾部填充
        padding_len = decrypted_data[-1]
        decrypted_data = decrypted_data[:-padding_len]

        return decrypted_data.decode("utf-8")
    
    def encrypt_data(data: str) -> str:
        # 解码 Base64 密钥
        key_bytes = b64decode(secret_key)

        # 创建 Blowfish 加密器（ECB 模式）
        cipher = Blowfish.new(key_bytes, Blowfish.MODE_ECB)

        # Blowfish 块大小为 8 字节，需填充明文
        block_size = Blowfish.block_size
        padded_data = pad(data.encode('utf-8'), block_size)

        # 加密
        encrypted_bytes = cipher.encrypt(padded_data)

        # 返回 Base64 编码字符串
        return b64encode(encrypted_bytes).decode('utf-8')
    
        
# 数据库单例
databae_manager = DatabaseManager()
