from asyncio import sleep
from shared.tinder.tinder_client import TinderClient


async def create_account():
    try:
        proxy = "KEn1A3:GGXJNr@185.79.133.112:8000"
        email = "samueloberon203013@xuanlich.com"
        phone_number = "66637129512"

        client = TinderClient(
            userAgent="Tinder/14.21.0 (iPhone; iOS 14.2.0; Scale/2.00)",
            platform="ios",
            tinderVersion="14.21.0",
            appVersion="5546",
            osVersion=140000200000,
            language="en-US",
            proxy=proxy
        )
        print("DEBUG: Initializing session...")
        buckets_response = client.sendBuckets()
        if not buckets_response:
            print("DEBUG: Failed to initialize session")
            return
        await sleep(2)

        login_response = client.authLogin(phone_number)
        if not login_response:
            print("DEBUG: No response from server")
            return False
        if 'error' in login_response:
            print(f"DEBUG: Login error: {login_response['error']}")
            return False

        otp = input("OTP: ")
        if not otp:
            print("DEBUG: Failed to obtain OTP code")
            return False

        print(f"DEBUG: Verifying OTP: {otp}")
        otp_response = client.verifyOtp(phone_number, otp)
        if 'error' not in otp_response:
            print("DEBUG: Phone verification successful!")
            print("DEBUG: Registering email...")
            email_response = client.useEmail(email)
            print("DEBUG: Email registration response:", json.dumps(email_response, indent=2))
            if 'error' not in email_response:
                print("DEBUG: Email registration successful!")
                print("DEBUG: Dismissing social connections...")
                dismiss_response = client.dismissSocialConnectionList()
                print("DEBUG: Dismiss response:", json.dumps(dismiss_response, indent=2))
                print("DEBUG: Getting authentication token...")
                auth_response = client.getAuthToken()
                print("DEBUG: Auth token response:", json.dumps(auth_response, indent=2))
                if 'error' not in auth_response:
                    print("AUTh SUCCESS")
                else:
                    return
            else:
                return
        else:
            return
        time.sleep(2)
        # Iniciar onboarding
        print("DEBUG: Starting onboarding process...")
        onboarding_response = client.startOnboarding()
        if not onboarding_response:
            print("DEBUG: Failed to start onboarding process")
            return
        time.sleep(2)
        # Configurar información básica
        print("DEBUG: Setting basic information...")
        user_info = get_user_info()
        info_response = client.onboardingSuper(
            user_info['name'],
            user_info['dob'],
            user_info['gender'],
            user_info['gender_interest']
        )
        if not info_response:
            print("DEBUG: Failed to set basic information")
            return
        time.sleep(2)
        # Ajustes adicionales del perfil
        print("DEBUG: Setting up additional profile settings...")
        setup_additional_profile_settings(client)
        time.sleep(2)
        # Subida de fotos
        # Comprobación de fotos
        print("DEBUG: Checking photos directory...")
        photos = get_photos_from_folder()
        if not photos:
            print("DEBUG: No photos found in the photos directory! Please add some photos and try again.")
            return
        print("DEBUG: Starting photo upload process...")
        upload_photos(client, photos)
        time.sleep(2)
        # Completar registro
        print("DEBUG: Completing registration...")
        complete_response = client.endOnboarding()
        print("DEBUG: Registration complete response:", json.dumps(debug_response(complete_response, client.last_status_code), indent=2))
        # Manejo de captcha, si es necesario
        if client.last_status_code != 200:
            print("DEBUG: Encountered a challenge. Attempting to resolve...")
            if client.processCaptcha():
                print("DEBUG: Challenge resolved successfully!")
            else:
                print("DEBUG: Failed to resolve challenge")
                return
        # Configuración de ubicación
        try:
            time.sleep(3)
            print("DEBUG: Configuring location settings...")
            ip = client.checkIp()
            print(f"DEBUG: Current IP: {ip}")
            lat, lng = client.getLocation(ip)
            print(f"DEBUG: Location detected - Latitude: {lat}, Longitude: {lng}")
            try_api_call(client, lambda: client.updateLocation(lat, lng), "Updating location")
            time.sleep(1)
            try_api_call(client, lambda: client.locInit(), "Initializing location services")
            time.sleep(1)
            try_api_call(client, lambda: client.updateLocalization(lat, lng), "Updating localization")
        except Exception as e:
            print(f"DEBUG: Warning: Could not set location automatically: {str(e)}")
        # Guardar sesión
        try:
            print("DEBUG: Saving session information...")
            session_info = client.toObject()
            session_file = f"tinder_session_{client.userId}.json"
            with open(session_file, "w") as f:
                json.dump(session_info, f, indent=2)
            print(f"DEBUG: Session saved to: {session_file}")
        except Exception as e:
            print(f"DEBUG: Warning: Could not save session information: {str(e)}")
        print("DEBUG: === Registration Summary ===")
        print("DEBUG: ✓ Basic registration completed")
        print("DEBUG: ✓ Photos uploaded successfully")
        print("DEBUG: ✓ Profile configured")
        print(f"DEBUG: ✓ Using IP: {client.checkIp()}")
        print(f"DEBUG: ✓ User ID: {client.userId}")
        credentials = {
            'user_id': client.userId,
            'email': user_info['email'],
            'registration_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'proxy_used': proxy,
            'ip_used': client.checkIp()
        }
        with open('tinder_credentials.json', 'a') as f:
            f.write(json.dumps(credentials) + '\n')
        print("DEBUG: Credentials saved to: tinder_credentials.json")
        print("DEBUG: You can now use the Tinder app with these credentials.")
    except Exception as e:
        print(f"DEBUG: An error occurred: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        print("DEBUG: Process completed!")
        if 'client' in locals() and hasattr(client, 'userId'):
            print(f"DEBUG: User ID: {client.userId}")