from typing import Container, Optional, Type, List, Dict, Any, Union
from pydantic import BaseConfig, BaseModel, create_model, Field
from sqlalchemy.inspection import inspect
from sqlalchemy.orm.properties import ColumnProperty
from sqlalchemy.sql.schema import ColumnDefault
from sqlalchemy.orm.relationships import RelationshipProperty

class OrmConfig(BaseConfig):
    orm_mode = True

def sqlalchemy_to_pydantic(
    db_model: Type,
    *,
    config: Type = OrmConfig,
    exclude: Container[str] = [],
    include_relationships: bool = False,
) -> Type[BaseModel]:
    mapper = inspect(db_model)
    fields: Dict[str, Any] = {}
    
    for attr in mapper.attrs:
        if isinstance(attr, ColumnProperty):
            if attr.key in exclude:
                continue
                
            column = attr.columns[0]
            python_type = None
            
            # Определяем тип Python
            if hasattr(column.type, "python_type"):
                python_type = column.type.python_type
            elif hasattr(column.type, "impl") and hasattr(column.type.impl, "python_type"):
                python_type = column.type.impl.python_type

            if not python_type:
                raise TypeError(f"Could not infer python type for column {column.name}")

            # Определяем значение по умолчанию
            default = ...
            if column.default is not None and isinstance(column.default, ColumnDefault):
                default = column.default.arg
            elif column.nullable:
                default = None
            elif column.server_default:
                default = Field(None)  # Для автогенерируемых значений
            else:
                default = ...

            # Для полей с дефолтными значениями
            if column.default and not column.nullable:
                default = column.default.arg if not callable(column.default.arg) else None

            fields[attr.key] = (
                Union[python_type, None] if column.nullable else python_type,
                default if default != ... else Field(...),
            )

    if include_relationships:
        for rel in mapper.relationships:
            if rel.key in exclude:
                continue
                
            related_model = rel.mapper.class_
            # Use lazy loading to avoid circular imports
            related_schema = sqlalchemy_to_pydantic(
                related_model,
                exclude=exclude,
                include_relationships=False
            )
            
            # Handle optional relationships (nullable ForeignKey)
            if rel.direction.name == 'MANYTOONE' and rel.uselist is False:
                fields[rel.key] = (Optional[related_schema], None)
            elif rel.uselist:
                fields[rel.key] = (List[related_schema], [])
            else:
                fields[rel.key] = (related_schema, None)

    return create_model(
        db_model.__name__,
        __config__=config,
        **fields
    )

def generate_crud_schemas(
    db_model: Type,
    exclude: Container[str] = []
) -> Dict[str, Type[BaseModel]]:
    base_config = OrmConfig
    base_schema = sqlalchemy_to_pydantic(
        db_model,
        config=base_config,
        include_relationships=True
    )

    create_exclude = set(exclude) | {col.name for col in inspect(db_model).primary_key}
    create_schema = sqlalchemy_to_pydantic(
        db_model,
        config=base_config,
        exclude=create_exclude,
        include_relationships=False
    )
    return {
        "Create": create_schema,
        "Update": create_schema,
        "Read": base_schema
    }