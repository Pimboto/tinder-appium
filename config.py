# config.py 

# API Key de DaisySMS
DAISYSMS_API_KEY = "KrnHzGtiRHvgdzwZFCADtVbm5fS6zq"
TINDER_SERVICE_CODE = "oi"

# Configuraciones de dispositivos
DEVICES = {
    "iphone": {
        "platformName": "iOS",
        "appium:automationName": "XCUITest",
        "appium:deviceName": "iPhone Pimbo",
        "appium:udid": "00008120-001C02E03CF1A01E",
    }
    # Puedes agregar más dispositivos aquí
}

# Datos de usuario de prueba
TEST_USER = {
    "phone_number": "auto",  # "auto" para usar DaisySMS, o un número específico
    "email": "cMilal_44@gmail.com",  # "auto" para generar automáticamente
    "first_name": "Mila",
    "birth_day": "04122003"
}

# XPaths organizados por secciones
XPATHS = {
    # Creación de cuenta
    "create_account_button": '//XCUIElementTypeButton[@name="create_account_button"]',
    "continue_button": '//XCUIElementTypeButton[@name="continue_button"]',
    "continue_button_alternative": '//XCUIElementTypeButton[@name="continueButton"]',
    "next_button": '//XCUIElementTypeButton[@name="next_button"]',
    "next_button_alternative": '//XCUIElementTypeButton[@name="Next"]',
    
    
    "skip_button": '//XCUIElementTypeButton[@name="skip_button"]',
    "skip_button_alternative": '//XCUIElementTypeButton[@name="SKIP"]',
    "agree_button": '//XCUIElementTypeButton[@name="button_onboarding_submit"]',
    
    # Configuración de fotos iniciales
    "skip_photos_button": '//XCUIElementTypeButton[@name="Skip"]',
    
    # Configuración de perfil básico
    "lets_go_button": '//XCUIElementTypeButton[@name="Let\'s go"]',
    
    # Fecha de nacimiento
    "button_onboarding_submit": '//XCUIElementTypeButton[@name="button_onboarding_submit"]',
    
    # Género
    "woman_button": '//XCUIElementTypeButton[@name="Woman"]',
    "show_gender_checkbox": '//XCUIElementTypeOther[@name="unchecked, Show gender on profile"]',
    
    # Orientación sexual
    "straight_button": '//XCUIElementTypeTable/XCUIElementTypeCell[1]',
    "show_sexual_orientation_checkbox": '//XCUIElementTypeOther[@name="unchecked, Show sexual orientation on profile"]',
    
    # Intereses
    "men_button": '//XCUIElementTypeButton[@name="Men"]',
    
    # Preferencia de distancia
    "distance_slider_value": '//XCUIElementTypeOther[@name="value"]',
    "distance_slider_line": '//XCUIElementTypeApplication[@name="Tinder"]/XCUIElementTypeWindow[1]/XCUIElementTypeOther[2]/XCUIElementTypeOther/XCUIElementTypeOther[1]/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeOther[2]/XCUIElementTypeOther[2]',
    
    # Lo que estás buscando
    "looking_for_option_3": '//XCUIElementTypeCollectionView/XCUIElementTypeCell[3]/XCUIElementTypeOther/XCUIElementTypeOther',
    
    # Educación
    "skip_education_button": '//XCUIElementTypeButton[@name="Skip"]',
    
    # Estilo de vida - Alcohol
    "alcohol_options": {
        "not_for_me": '//XCUIElementTypeButton[@name="Not for me"]',
        "sober": '//XCUIElementTypeButton[@name="Sober"]',
        "sober_curious": '//XCUIElementTypeButton[@name="Sober curious"]',
        "special_occasions": '//XCUIElementTypeButton[@name="On special occasions"]',
        "socially_weekends": '//XCUIElementTypeButton[@name="Socially on weekends"]',
        "most_nights": '//XCUIElementTypeButton[@name="Most Nights"]'
    },
    
    # Estilo de vida - Fumar
    "smoking_options": {
        "social_smoker": '//XCUIElementTypeButton[@name="Social smoker"]',
        "smoker_drinking": '//XCUIElementTypeButton[@name="Smoker when drinking"]',
        "non_smoker": '//XCUIElementTypeButton[@name="Non-smoker"]',
        "smoker": '//XCUIElementTypeButton[@name="Smoker"]',
        "trying_to_quit": '//XCUIElementTypeButton[@name="Trying to quit"]'
    },
    
    # Estilo de vida - Ejercicio
    "workout_options": {
        "everyday": '//XCUIElementTypeButton[@name="Everyday"]',
        "often": '//XCUIElementTypeButton[@name="Often"]',
        "sometimes": '//XCUIElementTypeButton[@name="Sometimes"]',
        "never": '//XCUIElementTypeButton[@name="Never"]'
    },
    
    # Estilo de vida - Mascotas
    "pets_options": {
        "dog": '//XCUIElementTypeButton[@name="Dog"]',
        "cat": '//XCUIElementTypeButton[@name="Cat"]',
        "reptile": '//XCUIElementTypeButton[@name="Reptile"]',
        "amphibian": '//XCUIElementTypeButton[@name="Amphibian"]',
        "bird": '//XCUIElementTypeButton[@name="Bird"]',
        "fish": '//XCUIElementTypeButton[@name="Fish"]',
        "dont_have_but_love": '//XCUIElementTypeButton[@name="Don\'t have but love"]',
        "other": '//XCUIElementTypeButton[@name="Other"]',
        "turtle": '//XCUIElementTypeButton[@name="Turtle"]',
        "hamster": '//XCUIElementTypeButton[@name="Hamster"]'
    },
    
    # Comunicación
    "communication_options": {
        "big_time_texter": '//XCUIElementTypeButton[@name="Big time texter"]',
        "phone_caller": '//XCUIElementTypeButton[@name="Phone caller"]',
        "video_chatter": '//XCUIElementTypeButton[@name="Video chatter"]',
        "bad_texter": '//XCUIElementTypeButton[@name="Bad texter"]',
        "better_in_person": '//XCUIElementTypeButton[@name="Better in person"]'
    },
    
    # Recibir amor
    "love_options": {
        "thoughtful_gestures": '//XCUIElementTypeButton[@name="Thoughtful gestures"]',
        "presents": '//XCUIElementTypeButton[@name="Presents"]',
        "touch": '//XCUIElementTypeButton[@name="Touch"]',
        "compliments": '//XCUIElementTypeButton[@name="Compliments"]',
        "time_together": '//XCUIElementTypeButton[@name="Time together"]'
    },
    
    # Educación
    "education_options": {
        "bachelors": '//XCUIElementTypeButton[@name="Bachelors"]',
        "in_college": '//XCUIElementTypeButton[@name="In College"]',
        "high_school": '//XCUIElementTypeButton[@name="High School"]',
        "phd": '//XCUIElementTypeButton[@name="PhD"]',
        "in_grad_school": '//XCUIElementTypeButton[@name="In Grad School"]',
        "masters": '//XCUIElementTypeButton[@name="Masters"]',
        "trade_school": '//XCUIElementTypeButton[@name="Trade School"]'
    },
    
    # Signo zodiacal
    "zodiac_options": {
        "capricorn": '//XCUIElementTypeButton[@name="Capricorn"]',
        "aquarius": '//XCUIElementTypeButton[@name="Aquarius"]',
        "pisces": '//XCUIElementTypeButton[@name="Pisces"]',
        "aries": '//XCUIElementTypeButton[@name="Aries"]',
        "taurus": '//XCUIElementTypeButton[@name="Taurus"]',
        "gemini": '//XCUIElementTypeButton[@name="Gemini"]',
        "cancer": '//XCUIElementTypeButton[@name="Cancer"]',
        "leo": '//XCUIElementTypeButton[@name="Leo"]',
        "virgo": '//XCUIElementTypeButton[@name="Virgo"]',
        "libra": '//XCUIElementTypeButton[@name="Libra"]'
    },
    
    # Intereses
    "interests": {
        "harry_potter": '(//XCUIElementTypeStaticText[@name="Harry Potter"])[1]',
        "heavy_metal": '(//XCUIElementTypeStaticText[@name="Heavy Metal"])[1]/XCUIElementTypeOther',
        "drama_shows": '(//XCUIElementTypeStaticText[@name="Drama shows"])[1]/XCUIElementTypeOther',
        "hockey": '(//XCUIElementTypeStaticText[@name="Hockey"])[1]/XCUIElementTypeOther',
        "home_workout": '(//XCUIElementTypeStaticText[@name="Home Workout"])[1]/XCUIElementTypeOther',
        "cafe_hopping": '(//XCUIElementTypeStaticText[@name="Cafe hopping"])[1]/XCUIElementTypeOther',
        "instagram": '(//XCUIElementTypeStaticText[@name="Instagram"])[1]/XCUIElementTypeOther',
        "language_exchange": '(//XCUIElementTypeStaticText[@name="Language Exchange"])[1]',
        "crime_shows": '(//XCUIElementTypeStaticText[@name="Crime shows"])[1]/XCUIElementTypeOther',
        "gym": '(//XCUIElementTypeStaticText[@name="Gym"])[1]/XCUIElementTypeOther',
        "soul_music": '(//XCUIElementTypeStaticText[@name="Soul music"])[1]/XCUIElementTypeOther',
        "shisha": '(//XCUIElementTypeStaticText[@name="Shisha"])[1]/XCUIElementTypeOther',
        "gospel_music": '(//XCUIElementTypeStaticText[@name="Gospel music"])[1]/XCUIElementTypeOther',
        "trying_new_things": '(//XCUIElementTypeStaticText[@name="Trying New Things"])[1]/XCUIElementTypeOther',
        "singing": '**/XCUIElementTypeStaticText[`name == "Singing"`][1]/XCUIElementTypeOther'
    },
    
    # Fotos
    "add_photos_button": '//XCUIElementTypeCollectionView/XCUIElementTypeCell[1]/XCUIElementTypeOther/XCUIElementTypeOther[2]',
    "gallery_button": '//XCUIElementTypeStaticText[@name="Gallery"]',
    "select_photos_button": '//XCUIElementTypeButton[@name="Select More Photos…"]',
    "selecciona_fotos_alert": '//XCUIElementTypeButton[@name="Keep Current Selection"]',
    "collections_button": '//XCUIElementTypeButton[@name="Collections"]',
    "model_album_button": '(//XCUIElementTypeStaticText[@name="Model"])[1]',
    "first_image": '(//XCUIElementTypeImage[@name="PXGGridLayout-Info"])[1]',
    "second_image": '(//XCUIElementTypeImage[@name="PXGGridLayout-Info"])[2]',
    "third_image": '(//XCUIElementTypeImage[@name="PXGGridLayout-Info"])[3]',
    "fourth_image": '(//XCUIElementTypeImage[@name="PXGGridLayout-Info"])[4]',
    "update_button": '//XCUIElementTypeButton[@name="Update"]',
    "recents_button": '//XCUIElementTypeTable/XCUIElementTypeCell[1]',
    "recents_first_image": '//XCUIElementTypeApplication[@name="Tinder"]/XCUIElementTypeWindow[1]/XCUIElementTypeOther[3]/XCUIElementTypeOther[2]/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeOther[1]/XCUIElementTypeOther/XCUIElementTypeCollectionView/XCUIElementTypeCell[1]',
    "recents_second_image": '//XCUIElementTypeApplication[@name="Tinder"]/XCUIElementTypeWindow[1]/XCUIElementTypeOther[3]/XCUIElementTypeOther[2]/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeOther[1]/XCUIElementTypeOther/XCUIElementTypeCollectionView/XCUIElementTypeCell[2]',
    "recents_third_image": '//XCUIElementTypeApplication[@name="Tinder"]/XCUIElementTypeWindow[1]/XCUIElementTypeOther[3]/XCUIElementTypeOther[2]/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeOther[1]/XCUIElementTypeOther/XCUIElementTypeCollectionView/XCUIElementTypeCell[3]',
    "recents_fourth_image": '//XCUIElementTypeApplication[@name="Tinder"]/XCUIElementTypeWindow[1]/XCUIElementTypeOther[3]/XCUIElementTypeOther[2]/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeOther[1]/XCUIElementTypeOther/XCUIElementTypeCollectionView/XCUIElementTypeCell[4]',
    "done_button": '//XCUIElementTypeButton[@name="Done"]',
    
    # Finalizando
    "close_button": '//XCUIElementTypeButton[@name="close"]',
    "no_notifications_button": '//XCUIElementTypeButton[@name="secondary_button_push_view"]',
    
    # Tutorial
    "start_tutorial_button": '//XCUIElementTypeButton[@name="Start tutorial"]',
    "like_button": '//XCUIElementTypeButton[@name="Like"]',
    "pass_button": '//XCUIElementTypeButton[@name="Pass"]',
    "lets_go_final_button": '//XCUIElementTypeButton[@name="Let\'s go"]'
}

# Configuración de tiempo
TIME_CONFIG = {
    "total_flow_time": 420,  # 10 minutos para todo el flujo
    "timeout": 20,          # segundos para esperar elementos
    "otp_timeout": 300      # segundos para esperar OTP
}