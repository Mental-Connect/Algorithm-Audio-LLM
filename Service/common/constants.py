# 数据库配置
mongo_host = "127.0.0.1"  # 主机名
mongo_port = "27017"  # 端口
mongo_username="backend"  # 账号
mongo_password="psycho_system12357"  # 密码
mongo_authentication="admin"  # 身份校验数据库
default_db ="mental_connect"  # 默认数据库
dabases=["mental_connect"]  # 所有数据库
mongo_connect_str = f"mongodb://{mongo_username}:{mongo_password}@{mongo_host}:{mongo_port}/{mongo_authentication}"
 