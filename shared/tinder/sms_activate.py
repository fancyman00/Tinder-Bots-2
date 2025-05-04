import aiohttp
import asyncio
import time

async def get_sms_activate_number(api_key, service="oi", country="16", forward=0):
    """
    Асинхронно запрашивает номер через API SMS Activate.
    """
    url = "https://api.sms-activate.ae/stubs/handler_api.php"
    params = {
        "api_key": api_key,
        "action": "getNumber",
        "service": service,
        "forward": forward,
        "country": country
    }
    print("DEBUG: Solicitando número a SMS Activate con parámetros:", params)
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=30)) as response:
                print("DEBUG: Código de estado de la respuesta:", response.status)
                print("DEBUG: Cabeceras de la respuesta:", response.headers)
                resp_text = await response.text()
                print("DEBUG: Texto de la respuesta:", resp_text)

                if response.status != 200:
                    print("DEBUG: El código de estado no es 200, se aborta la solicitud.")
                    return None

                resp_text = resp_text.strip()
                if resp_text.startswith("ACCESS_NUMBER:"):
                    parts = resp_text.split(":")
                    if len(parts) == 3:
                        activation_id = parts[1]
                        phone_number = parts[2]
                        print(f"DEBUG: Número recibido: {phone_number} (activationId: {activation_id})")
                        return {"activation_id": activation_id, "phone_number": phone_number}
                    else:
                        print("DEBUG: Formato de respuesta inesperado:", resp_text)
                        return None
                else:
                    print("DEBUG: Respuesta inesperada:", resp_text)
                    return None
    except Exception as e:
        print("DEBUG: Error al solicitar número de SMS Activate:", str(e))
        return None

async def poll_sms_code(api_key, activation_id, timeout=120, interval=5):
    """
    Асинхронно опрашивает API для получения SMS кода.
    """
    url = "https://api.sms-activate.ae/stubs/handler_api.php"
    params = {
        "api_key": api_key,
        "action": "getStatus",
        "id": activation_id
    }
    print("DEBUG: Esperando código SMS de SMS Activate...")
    start_time = time.time()
    
    async with aiohttp.ClientSession() as session:
        while True:
            if time.time() - start_time > timeout:
                print("DEBUG: Timeout al esperar el código SMS.")
                return None
            
            try:
                async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    resp_text = (await response.text()).strip()
                    print(f"DEBUG: Respuesta de SMS Activate: {resp_text}")
                    
                    if "STATUS_OK" in resp_text:
                        parts = resp_text.split(":")
                        if len(parts) == 2:
                            code = parts[1]
                            print(f"DEBUG: Código SMS recibido: {code}")
                            return code
            except Exception as e:
                print("DEBUG: Error al obtener estado SMS Activate:", str(e))
            
            await asyncio.sleep(interval)