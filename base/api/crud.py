from typing import Callable, Type, List
from fastapi import APIRouter, Depends, status
from base.database.crud import BaseCRUD
from base.tools.sa2py import generate_crud_schemas


def CRUDRouter[ModelType, CRUDType: BaseCRUD](
    Model: Type[ModelType],
    prefix: str = "/example",
    tags: list[str] = ["Example"],
    object_name: str = "Example",
    service_depend: Callable[[], CRUDType] = None,
    exclude: List[str] = []
) -> APIRouter:
    """
    Генерирует CRUD роутер для SQLAlchemy модели
    Args:
        Model: SQLAlchemy модель
        prefix: Префикс для маршрутов
        tags: Теги для OpenAPI документации
        object_name: Название сущности для документации
    Returns:
        APIRouter: Настроенный роутер с CRUD эндпоинтами
    """
    router = APIRouter(prefix=prefix, tags=tags)
    schemas = generate_crud_schemas(Model, exclude=exclude + ["id", "created_at", "updated_at"])

    CreateSchema = schemas["Create"]
    ReadSchema = schemas["Read"]
    UpdateSchema = schemas["Update"]

    # Регистрация эндпоинтов
    @router.post(
        "/",
        response_model=ReadSchema,
        status_code=status.HTTP_201_CREATED,
        summary=f"Создать новую {object_name}",
        description=f"Создание новой записи {object_name} в базе данных"
    )
    async def create_item(
        data: CreateSchema,
        manager: CRUDType = Depends(service_depend)
    ) -> ModelType:
        return await manager.add(data)

    @router.get(
        "/",
        response_model=List[ReadSchema],
        summary=f"Получить список {object_name}",
        description=f"Получение списка всех записей {object_name}"
    )
    async def read_items(
        limit: int = None,
        page:  int = None,
        manager: CRUDType = Depends(service_depend)
    ) -> List[ModelType]:
        return await manager.get_all(limit=limit, page=page)

    @router.get(
        "/{item_id}",
        response_model=ReadSchema,
        summary=f"Получить {object_name} по ID",
        description=f"Получение конкретной записи {object_name} по её идентификатору"
    )
    async def read_item(
        item_id: int,
        manager: CRUDType = Depends(service_depend)
    ) -> ModelType:
        return await manager.get(item_id)

    @router.put(
        "/{item_id}",
        summary=f"Обновить {object_name}",
        description=f"Обновление данных существующей записи {object_name}"
    )
    async def update_item(
        item_id: int,
        data: UpdateSchema,
        manager: CRUDType = Depends(service_depend)
    ) -> ModelType:
        return await manager.update(item_id, data)

    @router.delete(
        "/{item_id}",
        summary=f"Удалить {object_name}",
        description=f"Удаление конкретной записи {object_name} из базы данных",
    )
    async def delete_item(
        item_id: int,
        manager: CRUDType = Depends(service_depend)
    ) -> None:
        return await manager.delete(item_id)

    return router