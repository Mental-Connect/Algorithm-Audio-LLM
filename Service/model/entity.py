
from enum import Enum

# 当前提取的实体类型
class EntityType(str, Enum):
    person = "person"  # 人名
    
class Entity:
    user_name: str = None
    
entity_enum_values = [item.name for item in EntityType]
