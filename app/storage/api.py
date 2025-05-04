import json
from storage.dependencies import get_storage
from storage.service import SettingsRedisStorage
from storage.schemas import SettingValue
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/settings", tags=["Settings"])

@router.get("/{key}")
async def get_setting(
    key: str, 
    redis: SettingsRedisStorage = Depends(get_storage)
):
    try:
        value = await redis.get_setting(key)
        if value is None:
            raise HTTPException(status_code=404, detail="Setting not found")
        return {"key": key, "value": value}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"message": f"Redis error: {str(e)}"}
        )

@router.post("/{key}")
async def set_setting(
    key: str,
    setting: SettingValue,
    redis: SettingsRedisStorage = Depends(get_storage)
):
    try:
        await redis.set_setting(key, setting.value, setting.ttl)
        return {"status": "success", "key": key}
    except json.JSONDecodeError:
        raise HTTPException(400, "Invalid JSON format")
    except Exception as e:
        raise HTTPException(500, f"Storage error: {str(e)}")

@router.delete("/{key}")
async def delete_setting(
    key: str,
    redis: SettingsRedisStorage = Depends(get_storage)
):
    await redis.delete_setting(key)
    return {"status": "deleted", "key": key}

@router.get("/")
async def get_all_settings(
    redis: SettingsRedisStorage = Depends(get_storage)
):
    try:
        settings = await redis.get_all_settings()
        return {"settings": settings}
    except Exception as e:
        raise HTTPException(500, f"Error retrieving settings: {str(e)}")    