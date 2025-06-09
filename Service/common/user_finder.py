from pypinyin import lazy_pinyin
from rapidfuzz import fuzz, process
from Service.database.database_manager import databae_manager


# 姓名查询和匹配
class UserFinder():
    pinyin_weight = 0.6  # 拼音距离权重
    edit_weight = 0.4  # 编辑距离权重
    threshold = 60.0  # 相似阈值, 大于这个值被视为两个姓名相似
    def __init__(self):
        self.__update_names_db()
    
    # 更新学生姓名库
    def __update_names_db(self):
        self.names_db = databae_manager.get_student_names()
        # self.names_pinyin_db = {}
        # for school_id, names in self.names_db.items():
        #     names_pinyin = [self.__name_to_pinyin(name) for name in names]
        #     self.names_pinyin_db[school_id] = names_pinyin
        
    # 文字转拼音
    # name 输入的学生姓名
    def __name_to_pinyin(name:str) -> str:
        return ''.join(lazy_pinyin(name))
    
    # 根据姓名和学校查询最相似的姓名
    # name 原姓名
    # school_id 所在学校id
    # size 查询的数据条数,默认3条
    def get_match_names(self, input_name:str, school_id:str, size = 3) -> list[str]:
        names = self.names_db[school_id]
        scored = []
        # 对比库中的姓名计算相似度
        for name in names:
            score = self.similarity_score(input_name, name)
            if score >= self.threshold:
                scored.append((input_name, score))
                
        # 排序并返回
        return sorted(scored,key=lambda x: x[1], reverse=True)[:size]
    
    # 计算结合编辑距离和拼音距离的加权得分
    # input_name 对比的文本
    # candidate_name 被对比的文本
    def similarity_score(self, input_name: str, candidate_name: str) -> float:
        text_score = fuzz.ratio(input_name, candidate_name)
        pinyin_score = fuzz.ratio(self.__name_to_pinyin(input_name), self.__name_to_pinyin(candidate_name))
        return self.edit_weight * text_score + self.pinyin_weight * pinyin_score
        
        
    # 根据姓名查询最相似的姓名
    # name 原姓名
    # size 查询的数据条数,默认3条
    def get_match_names(self, input_name:str, size = 3) -> list[str]:
        # 归并所有表中的学生姓名并去重
        names_set = set()
        for school_id, db_names in self.names_db.items():
            names_set(tuple(db_names))
        names = list(names_set)
        
        # 对比库中的姓名计算相似度
        scored = []
        for name in names:
            score = self.similarity_score(input_name, name)
            if score >= self.threshold:
                scored.append((input_name, score))
        
        # 排序并返回
        return sorted(scored,key=lambda x: x[1], reverse=True)[:size]