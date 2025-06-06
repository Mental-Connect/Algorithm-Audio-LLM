
# 姓名查询和匹配
class NameMatcher():
    def __init__(self, names):
        self.names_db = names        
    
    # 根据姓名和学校查询最相似的姓名
    # name 原姓名
    # school_id 所在学校id
    # size 查询的数据条数,默认3条
    def get_match_names(name:str, school_id:str, size = 3) -> list[str]:
        pass
    
    # 根据姓名查询最相似的姓名
    # name 原姓名
    # size 查询的数据条数,默认3条
    def get_match_names(name:str, size = 3) -> list[str]:
        pass

    
