# modules/account_creation.py
from config import XPATHS
from sms_service import SMSService
import time
import logging
import random
import string
from appium.webdriver.common.mobileby import MobileBy
from appium import webdriver



def create_account(bot):
    """Módulo: Crear cuenta"""
    bot.logger.info("Iniciando módulo: Crear cuenta")
    bot.state['current_module'] = 'create_account'
    bot.save_checkpoint()
    
    # Hacer clic en botón de crear cuenta
    if not bot.click_element(XPATHS["create_account_button"]):
        return False
    
    bot.state['create_account_completed'] = True
    bot.save_checkpoint()
    
    # Aplicar el delay después de completar este paso
    bot.apply_step_delay()
    
    return True

def enter_phone_number(bot, phone_number, api_key=None, service_code=None):
    """
    Módulo: Ingresar número de teléfono
    
    Args:
        bot: Instancia de TinderAutomation
        phone_number: Número de teléfono o "auto" para usar DaisySMS
        api_key: API key de DaisySMS (si phone_number es "auto")
        service_code: Código de servicio para Tinder en DaisySMS
    """
    if bot.state.get('create_account_completed', False) is False:
        bot.logger.warning("Se debe completar 'create_account' primero")
        return False
        
    bot.logger.info("Iniciando módulo: Ingresar número de teléfono")
    bot.state['current_module'] = 'enter_phone_number'
    bot.save_checkpoint()
    
    # Si está configurado para usar DaisySMS
    if phone_number == "auto" and api_key:
        try:
            sms = SMSService(api_key, service_code)
            sufficient, balance = sms.has_sufficient_balance()
            
            if not sufficient:
                bot.logger.error(f"Saldo insuficiente en DaisySMS: ${balance}")
                return False
                
            activation_id, phone_number = sms.rent_number(carrier='vz')
            if not activation_id:
                bot.logger.error("No se pudo obtener un número de teléfono")
                return False
                
            bot.logger.info(f"Número obtenido: {phone_number}")
            bot.state['sms_activation_id'] = activation_id
            bot.state['daisy_sms_used'] = True
        except Exception as e:
            bot.logger.error(f"Error al obtener número de DaisySMS: {str(e)}")
            return False
    
    # Ingresar el número de teléfono usando el método centralizado
    if not bot.type_text(phone_number):
        bot.logger.error("No se pudo ingresar el número de teléfono")
        return False
    
    # Esperar un momento para asegurarse de que se ingresó correctamente
    time.sleep(2)
    
    # Clic en botón continuar
     # Clic en botón continuar
    if not bot.find_and_click_any_button([
        "continue_button",
        "continue_button_alternative",
        "next_button",
        "next_button_alternative"]):
        bot.logger.error("No se pudo hacer clic en ningún botón de continuar")
        return False
        
    
    bot.state['phone_number_entered'] = True
    bot.state['phone_number'] = phone_number
    bot.save_checkpoint()
    
    # Aplicar el delay después de completar este paso
    bot.apply_step_delay()
    
    return True

def enter_otp(bot, otp=None, api_key=None, timeout=300):
    """
    Módulo: Ingresar código OTP
    
    Args:
        bot: Instancia de TinderAutomation
        otp: Código OTP o None para obtenerlo de DaisySMS
        api_key: API key de DaisySMS
        timeout: Tiempo máximo de espera para el OTP
    """
    if bot.state.get('phone_number_entered', False) is False:
        bot.logger.warning("Se debe completar 'enter_phone_number' primero")
        return False
        
    bot.logger.info("Iniciando módulo: Ingresar OTP")
    bot.state['current_module'] = 'enter_otp'
    bot.save_checkpoint()
    
    # Si no hay OTP y se usó DaisySMS
    if not otp and bot.state.get('daisy_sms_used', False) and api_key:
        try:
            sms = SMSService(api_key, '')  # No necesitamos service_code para obtener OTP
            activation_id = bot.state.get('sms_activation_id')
            
            if not activation_id:
                bot.logger.error("No se encontró ID de activación")
                return False
                
            bot.logger.info(f"Esperando código OTP para ID {activation_id}...")
            otp = sms.get_sms_code(activation_id, timeout=timeout)
            
            if not otp:
                bot.logger.error("No se pudo obtener el código OTP")
                return False
                
            bot.logger.info(f"Código OTP recibido: {otp}")
            sms.mark_as_done(activation_id)
            
        except Exception as e:
            bot.logger.error(f"Error al obtener OTP de DaisySMS: {str(e)}")
            return False
    elif not otp:
        # Si no hay OTP automático, pedir al usuario
        bot.logger.info("Esperando a que el usuario ingrese el OTP...")
        otp = input("Ingrese el código OTP recibido: ")
    
    # Ingresar el OTP usando el método centralizado
    if not bot.type_text(otp):
        bot.logger.error("No se pudo ingresar el código OTP")
        return False
    
    # Esperar un momento para asegurarse de que se ingresó correctamente
    time.sleep(1)
    
     # Clic en botón continuar
     # Clic en botón continuar
    if not bot.find_and_click_any_button([
        "continue_button",
        "continue_button_alternative",
        "next_button",
        "next_button_alternative"]):
        bot.logger.error("No se pudo hacer clic en ningún botón de continuar")
        return False
    
    bot.state['otp_entered'] = True
    bot.save_checkpoint()
    
    # Aplicar el delay después de completar este paso
    bot.apply_step_delay()
    
    return True

def generate_email(first_name):
    """Genera un correo electrónico en el formato especificado"""
    # Generar un carácter aleatorio
    random_char = random.choice(string.ascii_lowercase)
    
    # Generar dos números aleatorios
    random_nums = ''.join(random.choices(string.digits, k=2))
    
    # Crear el email en el formato nombre{char}_{números}@gmail.com
    email = f"{first_name.lower()}{random_char}_{random_nums}@gmail.com"
    
    return email

def enter_email(bot, email=None, first_name=None):
    """
    Módulo: Ingresar email
    
    Args:
        bot: Instancia de TinderAutomation
        email: Email específico o None para generar uno automáticamente
        first_name: Nombre para generar el email si email=None
    """
    if bot.state.get('otp_entered', False) is False:
        bot.logger.warning("Se debe completar 'enter_otp' primero")
        return False
        
    bot.logger.info("Iniciando módulo: Ingresar email")
    bot.state['current_module'] = 'enter_email'
    bot.save_checkpoint()
    
    # Generar un email si no se proporciona uno
    if not email and first_name:
        email = generate_email(first_name)
        bot.logger.info(f"Email generado automáticamente: {email}")
    elif not email:
        email = generate_email("user")
        bot.logger.info(f"Email generado automáticamente sin nombre: {email}")
    
    # Ingresar el email usando el método centralizado
    if not bot.type_text(email):
        bot.logger.error("No se pudo ingresar el email")
        return False
    
    # Esperar un momento para asegurarse de que se ingresó correctamente
    time.sleep(5)
    
     # Clic en botón continuar
    if not bot.find_and_click_any_button([
        "continue_button",
        "continue_button_alternative",
        "next_button",
        "next_button_alternative"]):
        bot.logger.error("No se pudo hacer clic en ningún botón de continuar")
        return False
    
    bot.state['email_entered'] = True
    bot.state['email'] = email
    bot.save_checkpoint()
    
    # Aplicar el delay después de completar este paso
    bot.apply_step_delay()
    
    return True

def skip_contact(bot):
    """Módulo: Saltar acceso a contactos"""
    if bot.state.get('email_entered', False) is False:
        bot.logger.warning("Se debe completar 'enter_email' primero")
        return False
        
    bot.logger.info("Iniciando módulo: Saltar acceso a contactos")
    bot.state['current_module'] = 'skip_contact'
    bot.save_checkpoint()
    
    # Clic en botón saltar
    if not bot.find_and_click_any_button([
        "skip_button",
        "skip_button_alternative"
        ]):
        bot.logger.error("No se pudo hacer clic en ningún botón de continuar")
        return False
    
    bot.state['contact_skipped'] = True
    bot.save_checkpoint()
    
    # Aplicar el delay después de completar este paso
    bot.apply_step_delay()
    
    return True

def accept_terms(bot):
    """Módulo: Aceptar términos y condiciones"""
    if bot.state.get('contact_skipped', False) is False:
        bot.logger.warning("Se debe completar 'skip_contact' primero")
        return False
        
    bot.logger.info("Iniciando módulo: Aceptar términos")
    bot.state['current_module'] = 'accept_terms'
    bot.save_checkpoint()
    
    # Clic en botón aceptar
    if not bot.click_element(XPATHS["agree_button"]):
        return False
    
    bot.state['terms_accepted'] = True
    bot.save_checkpoint()
    
    # Aplicar el delay después de completar este paso
    bot.apply_step_delay()
    
    return True

def skip_photo_selection(bot):
    """Módulo: Saltar la selección de fotos inicial"""
    if bot.state.get('terms_accepted', False) is False:
        bot.logger.warning("Se debe completar 'accept_terms' primero")
        return False
        
    bot.logger.info("Iniciando módulo: Saltar selección de fotos inicial")
    bot.state['current_module'] = 'skip_photo_selection'
    bot.save_checkpoint()
    
    # Clic en botón Skip
    if not bot.click_element(XPATHS["skip_photos_button"]):
        bot.logger.warning("No se pudo saltar la selección de fotos inicial, intentando continuar")
        return False
    
    bot.state['photo_selection_skipped'] = True
    bot.save_checkpoint()
    
    # Aplicar el delay después de completar este paso
    bot.apply_step_delay()
    
    return True 