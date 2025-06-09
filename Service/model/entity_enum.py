# 当前提取的实体类型
from enum import Enum


class EntityEnum(str, Enum):
    person = "person"  # 人名
    
# 实体中的所有参数名
entity_enum_values = [item.name for item in EntityEnum]