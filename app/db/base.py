from sqlalchemy.orm import declarative_base
from sqlalchemy import MetaData
# Хз как описать, но короче для корректной работы с сущностями все классы должны наследоваться 
# от BASE а все таблицы должны принимать мараметр metadata
# и тогда всё будет чики пуки
metadata = MetaData()
Base = declarative_base(metadata=metadata)