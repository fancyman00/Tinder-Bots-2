# from tinder_client import TinderClient
import json
import time
import random
import os
from datetime import datetime, date
import imghdr
from loguru import logger
import requests

from shared.tinder.tinder_client import TinderClient

# ============================
# Funciones para SMS Activate
# ============================
SMS_API_KEY = ""  # Reemplaza por tu clave

def get_sms_activate_number(api_key, service="oi", country="16", forward=0):
    """
    Solicita un número a la API de SMS Activate. Se espera una respuesta en texto plano con el formato:
      ACCESS_NUMBER:<activationId>:<phoneNumber>
    """
    url = "https://api.sms-activate.ae/stubs/handler_api.php"
    params = {
        "api_key": api_key,
        "action": "getNumber",
        "service": service,
        "forward": forward,
        "country": country
    }
    logger.debug("Solicitando número a SMS Activate con parámetros:", params)
    try:
        response = requests.get(url, params=params, timeout=30)
        logger.debug("Código de estado de la respuesta:", response.status_code)
        logger.debug("Cabeceras de la respuesta:", response.headers)
        logger.debug("Texto de la respuesta:", response.text)
        
        if response.status_code != 200:
            logger.debug("El código de estado no es 200, se aborta la solicitud.")
            return None

        resp_text = response.text.strip()
        if resp_text.startswith("ACCESS_NUMBER:"):
            parts = resp_text.split(":")
            if len(parts) == 3:
                activation_id = parts[1]
                phone_number = parts[2]
                logger.debug(f"Número recibido: {phone_number} (activationId: {activation_id})")
                return {"activation_id": activation_id, "phone_number": phone_number}
            else:
                logger.debug("Formato de respuesta inesperado:", resp_text)
                return None
        else:
            logger.debug("Respuesta inesperada:", resp_text)
            return None
    except Exception as e:
        logger.debug("Error al solicitar número de SMS Activate:", str(e))
        return None

def poll_sms_code(api_key, activation_id, timeout=120, interval=5):
    """
    Realiza polling para obtener el código SMS. Se espera recibir una respuesta en texto plano
    con el formato "STATUS_OK:<code>".
    """
    url = "https://api.sms-activate.ae/stubs/handler_api.php"
    params = {
        "api_key": api_key,
        "action": "getStatus",
        "id": activation_id
    }
    logger.debug("Esperando código SMS de SMS Activate...")
    waited = 0
    while waited < timeout:
        try:
            response = requests.get(url, params=params, timeout=30)
            resp_text = response.text.strip()
            logger.debug(f"Respuesta de SMS Activate: {resp_text}")
            if "STATUS_OK" in resp_text:
                parts = resp_text.split(":")
                if len(parts) == 2:
                    code = parts[1]
                    logger.debug(f"Código SMS recibido: {code}")
                    return code
            time.sleep(interval)
            waited += interval
        except Exception as e:
            logger.debug("Error al obtener estado SMS Activate:", str(e))
            time.sleep(interval)
            waited += interval
    logger.debug("Timeout al esperar el código SMS.")
    return None

# ============================
# Funciones de Imágenes y Directorio de Fotos
# ============================
def check_image_file(file_path):
    try:
        with open(file_path, 'rb') as f:
            data = f.read()
            image_type = imghdr.what(None, h=data)
            if image_type in ['jpeg', 'jpg', 'png']:
                file_size_mb = len(data) / (1024 * 1024)
                logger.debug(f"Image size: {file_size_mb:.2f}MB")
                if file_size_mb > 5:
                    print(f"Warning: Image is quite large ({file_size_mb:.2f}MB). This may increase upload time.")
                return True, data, len(data)
    except Exception as e:
        print(f"Error reading image {file_path}: {str(e)}")
    return False, None, 0

def get_photos_from_folder(photos_dir):
    logger.debug(f"Checking photos directory: {os.path.abspath(photos_dir)}")
    if not os.path.exists(photos_dir):
        print(f"Error: {photos_dir} directory not found!")
        return []
    valid_extensions = ('.jpg', '.jpeg', '.png')
    photos = []
    logger.debug("Scanning for photos:")
    files = sorted(os.listdir(photos_dir))
    for file in files:
        if file.lower().endswith(valid_extensions):
            file_path = os.path.join(photos_dir, file)
            logger.debug(f"Checking file: {file}")
            logger.debug(f"Full path: {os.path.abspath(file_path)}")
            is_valid, image_data, size = check_image_file(file_path)
            if is_valid and image_data:
                photos.append(image_data)
                logger.debug(f"Valid image found: {file} (Size: {size/1024/1024:.2f}MB)")
            else:
                logger.debug(f"Invalid or corrupted image: {file}")
            if len(photos) >= 9:
                logger.debug("Maximum number of photos (9) reached. Additional photos will be ignored.")
                break
    logger.debug(f"Total valid photos found: {len(photos)}")
    if len(photos) == 0:
        raise Exception("Please add some photos to the 'photos' directory")
    elif len(photos) < 2:
        raise Exception("Warning: Tinder requires at least 2 photos")
    return photos

def debug_response(response, status_code):
    logger.debug(f"Status Code: {status_code}")
    logger.debug("Raw Response:", response)
    try:
        if response:
            return json.loads(response)
        return None
    except json.JSONDecodeError:
        logger.debug("Response is not valid JSON")
        return None

# ============================
# Funciones de Autenticación y Registro
# ============================
def handle_auth_process(client, email):
    """
    Automatiza el proceso de autenticación usando SMS Activate:
      - Solicita número y polling para OTP
      - Registra email, descarta conexiones sociales y obtiene token de auth
    """
    # Se solicita el número vía SMS Activate
    sms_data = get_sms_activate_number(SMS_API_KEY)
    if not sms_data:
        print("Error al obtener número de SMS Activate")
        return False
    phone_number = sms_data["phone_number"]
    activation_id = sms_data["activation_id"]
    logger.debug(f"Using phone number: {phone_number} for authentication")
    
    logger.debug(f"Attempting login with {phone_number}...")
    login_response = client.authLogin(phone_number)
    if not login_response:
        logger.debug("No response from server")
        return False
    if 'error' in login_response:
        logger.debug(f"Login error: {login_response['error']}")
        return False

    # Automatizamos la verificación OTP con polling
    otp = poll_sms_code(SMS_API_KEY, activation_id)
    if not otp:
        logger.debug("Failed to obtain OTP code")
        return False

    logger.debug(f"Verifying OTP: {otp}")
    otp_response = client.verifyOtp(phone_number, otp)
    if 'error' not in otp_response:
        logger.debug("Phone verification successful!")
        logger.debug("Registering email...")
        email_response = client.useEmail(email)
        logger.debug("Email registration response:", json.dumps(email_response, indent=2))
        if 'error' not in email_response:
            logger.debug("Email registration successful!")
            logger.debug("Dismissing social connections...")
            dismiss_response = client.dismissSocialConnectionList()
            logger.debug("Dismiss response:", json.dumps(dismiss_response, indent=2))
            logger.debug("Getting authentication token...")
            auth_response = client.getAuthToken()
            logger.debug("Auth token response:", json.dumps(auth_response, indent=2))
            if 'error' not in auth_response:
                return True
    logger.debug("Authentication step failed.")
    return False

def handle_401_error(client):
    """Handles 401 error by refreshing auth token."""
    try:
        logger.debug("Refreshing authentication token...")
        auth_response = client.getAuthToken()
        if auth_response and 'error' not in auth_response:
            logger.debug("Successfully refreshed authentication token")
            return True
        logger.debug("Failed to refresh authentication token")
        return False
    except Exception as e:
        logger.debug(f"Error refreshing token: {str(e)}")
        return False

def upload_photos(client, photos):
    max_photos = min(len(photos), 9)
    print(f"DEBUG: Preparing to upload {max_photos} photos...")
    for i, photo_data in enumerate(photos[:max_photos], 1):
        max_retries = 3
        retry_count = 0
        token_refresh_attempted = False
        while retry_count < max_retries:
            try:
                print(f"DEBUG: Attempt {retry_count + 1} of {max_retries}")
                delay = random.uniform(1.0, 1.5)
                time.sleep(delay)
                response = client.onboardingPhoto(photo_data, max_photos)
                response_data = debug_response(response, client.last_status_code)
                if response_data and response_data.get('meta', {}).get('status') == 200:
                    print(f"DEBUG: Successfully uploaded photo {i}")
                    token_refresh_attempted = False
                    break
                elif client.last_status_code == 401 and not token_refresh_attempted:
                    print("DEBUG: Received 401 unauthorized error")
                    if handle_401_error(client):
                        token_refresh_attempted = True
                        continue
                    else:
                        print("DEBUG: Token refresh failed")
                retry_count += 1
                retry_delay = random.uniform(2.0, 3.0)
                time.sleep(retry_delay)
            except Exception as e:
                print(f"DEBUG: Error uploading photo {i}: {str(e)}")
                retry_count += 1
                time.sleep(2)
        if retry_count >= max_retries:
            raise Exception("Can not upload photos")
        if i < max_photos:
            delay = random.uniform(1.0, 1.5)
            print(f"DEBUG: Waiting {delay:.2f} seconds before next upload...")
            time.sleep(delay)

def try_api_call(client, func, description, max_retries=3, delay=2):
    """Función genérica para llamadas API con reintentos."""
    for attempt in range(max_retries):
        try:
            if attempt > 0:
                logger.debug(f"Retry attempt {attempt + 1}/{max_retries}")
            result = func()
            if result and client.last_status_code == 200:
                logger.debug(f"✓ {description} completed successfully")
                return True
            raise Exception(f"API call failed with status {client.last_status_code}")
        except Exception as e:
            if attempt < max_retries - 1:
                logger.debug(f"Retrying {description} in {delay} seconds...")
                time.sleep(delay)
            else:
                logger.debug(f"Failed to {description}: {str(e)}")
                return False
    return False


def setup_additional_profile_settings(client):
    """Configura ajustes adicionales del perfil (educación, zodiac, intereses, etc.)"""
    try:
        logger.debug("Setting up additional profile information...")
        relationship_data = {
            "fields": [{
                "name": "relationship_intent",
                "data": {
                    "selected_descriptors": [{
                        "id": "de_29",
                        "choice_selections": [{"id": "2"}]
                    }]
                }
            }]
        }
        client._onboarding_set(json.dumps(relationship_data).encode())
        time.sleep(1)
        education_data = {
            "fields": [{
                "name": "education",
                "data": {
                    "selected_descriptors": [{
                        "id": "de_4",
                        "choice_selections": [{"id": "1"}]
                    }]
                }
            }]
        }
        client._onboarding_set(json.dumps(education_data).encode())
        time.sleep(1)
        zodiac_data = {
            "fields": [{
                "name": "zodiac",
                "data": {
                    "selected_descriptors": [{
                        "id": "de_1",
                        "choice_selections": [{"id": "1"}]
                    }]
                }
            }]
        }
        client._onboarding_set(json.dumps(zodiac_data).encode())
        time.sleep(1)
        interests_data = {
            "fields": [{
                "name": "user_interests",
                "data": {
                    "selected_interests": [
                        {"id": "it_7", "name": "Travel"},
                        {"id": "it_9", "name": "Movies"},
                        {"id": "it_28", "name": "Reading"}
                    ]
                }
            }]
        }
        client._onboarding_set(json.dumps(interests_data).encode())
        logger.debug("✓ Additional profile settings configured")
        return True
    except Exception as e:
        logger.debug(f"Warning: Could not set additional profile settings: {str(e)}")
        return False

