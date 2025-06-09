from pymongo import MongoClient
from Service.common.constants import mongo_connect_str
from Service.common.constants import default_db


class DatabaseManager():
    school_user_collection_prefix = "school_user_"
    account_collection = "account"
    def __init__(self) -> None:
        self.client = MongoClient(mongo_connect_str)  # 初始化连接
        self.db = self.get_db()  # 初始化默认数据库
    
    # insert the data method.
    def insert_data():
        pass

    # remove the data method.
    def remove_data():
        pass

    
    # Update the data method
    def update_data():
        pass
    
    # 根据姓名查询学生
    # name 学生姓名
    def get_school_user(self, name:str):
        user_collection_names = self.get_user_collection_names()
        result = []
        for collection_name in user_collection_names:
            collection = self.db[collection_name]
            result.append(collection.find({"name": name}))
        return result
    
    # 根据姓名和所在学校查询学生
    # name 学生姓名
    def get_school_user(self, name:str, school_id:str):
        collection_name = f"{self.school_user_collection_prefix}{school_id}"
        collection = self.db[collection_name]
        return collection.find({"name": name})
    
    # 根据姓名和所在班级查询学生
    # name 学生姓名
    # class_id 班级id
    def get_school_user(self, name:str, class_id:str):
        user_collction_names = self.get_user_collection_names()
        results = []
        for collection_name in user_collction_names:
            collection = self.db[collection_name]
            results.append(collection.find({"name": name,"org":class_id}))
        return results
         
    
    # 根据姓名,所在学校,所在班级查询学生
    def get_school_user(self, name:str, school_id:str, class_id):
        collection_name = f"{self.school_user_collection_prefix}{school_id}"
        collection = self.db[collection_name]
        return collection.find({"name": name,"org":class_id})
        
    
    # 获取指定数据库名的数据库对象
    # db_name 数据库名
    def get_db(self, db_name = default_db):
        db = self.client[db_name]
        return db
            
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
        return [name for name in collection_names if name.startswith(self.school_user_collection_prefix)]

# 数据库单例
databae_manager = DatabaseManager()
