# modules/preferences.py
import random
import time
from config import XPATHS

def select_looking_for(bot):
    """Módulo: Seleccionar qué estás buscando"""
    if bot.state.get('distance_preference_set', False) is False:
        bot.logger.warning("Se debe completar 'set_distance_preference' primero")
        return False
        
    bot.logger.info("Iniciando módulo: Seleccionar qué estás buscando")
    bot.state['current_module'] = 'select_looking_for'
    bot.save_checkpoint()
    
    # Seleccionar la opción 3
    if not bot.click_element(XPATHS["looking_for_option_3"]):
        return False
    
    # Clic en botón continuar
    if not bot.click_element(XPATHS["button_onboarding_submit"]):
        return False
    
    bot.state['looking_for_selected'] = True
    bot.save_checkpoint()
    
    # Aplicar el delay después de completar este paso
    bot.apply_step_delay()
    
    return True

def skip_education(bot):
    """Módulo: Saltar la parte de educación"""
    if bot.state.get('looking_for_selected', False) is False:
        bot.logger.warning("Se debe completar 'select_looking_for' primero")
        return False
        
    bot.logger.info("Iniciando módulo: Saltar educación")
    bot.state['current_module'] = 'skip_education'
    bot.save_checkpoint()
    
    # Clic en botón saltar
    if not bot.click_element(XPATHS["skip_education_button"]):
        return False
    
    bot.state['education_skipped'] = True
    bot.save_checkpoint()
    
    # Aplicar el delay después de completar este paso
    bot.apply_step_delay()
    
    return True

def select_lifestyle_preferences(bot):
    """Módulo: Seleccionar preferencias de estilo de vida"""
    if bot.state.get('education_skipped', False) is False:
        bot.logger.warning("Se debe completar 'skip_education' primero")
        return False
        
    bot.logger.info("Iniciando módulo: Seleccionar preferencias de estilo de vida")
    bot.state['current_module'] = 'select_lifestyle'
    bot.save_checkpoint()
    
    # Seleccionar alcohol (aleatorio)
    alcohol_options = list(XPATHS["alcohol_options"].values())
    random_alcohol = random.choice(alcohol_options)
    if not bot.click_element(random_alcohol):
        bot.logger.warning("No se pudo seleccionar preferencia de alcohol, intentando continuar")
    
    # Seleccionar fumar (aleatorio)
    smoking_options = list(XPATHS["smoking_options"].values())
    random_smoking = random.choice(smoking_options)
    if not bot.click_element(random_smoking):
        bot.logger.warning("No se pudo seleccionar preferencia de fumar, intentando continuar")
    
    # Seleccionar ejercicio (aleatorio)
    workout_options = list(XPATHS["workout_options"].values())
    random_workout = random.choice(workout_options)
    if not bot.click_element(random_workout):
        bot.logger.warning("No se pudo seleccionar preferencia de ejercicio, intentando continuar")
    
    # Seleccionar mascotas (aleatorio)
    pets_options = list(XPATHS["pets_options"].values())
    random_pet = random.choice(pets_options)
    if not bot.click_element(random_pet):
        bot.logger.warning("No se pudo seleccionar preferencia de mascotas, intentando continuar")
    
    # Clic en botón continuar
    if not bot.click_element(XPATHS["button_onboarding_submit"]):
        return False
    
    bot.state['lifestyle_selected'] = True
    bot.save_checkpoint()
    
    # Aplicar el delay después de completar este paso
    bot.apply_step_delay()
    
    return True

def select_personal_info(bot):
    """Módulo: Seleccionar información personal adicional"""
    if bot.state.get('lifestyle_selected', False) is False:
        bot.logger.warning("Se debe completar 'select_lifestyle' primero")
        return False
        
    bot.logger.info("Iniciando módulo: Seleccionar información personal adicional")
    bot.state['current_module'] = 'select_personal_info'
    bot.save_checkpoint()
    
    # Seleccionar estilo de comunicación (aleatorio)
    communication_options = list(XPATHS["communication_options"].values())
    random_communication = random.choice(communication_options)
    if not bot.click_element(random_communication):
        bot.logger.warning("No se pudo seleccionar estilo de comunicación, intentando continuar")
    
    # Seleccionar cómo recibe amor (aleatorio)
    love_options = list(XPATHS["love_options"].values())
    random_love = random.choice(love_options)
    if not bot.click_element(random_love):
        bot.logger.warning("No se pudo seleccionar cómo recibe amor, intentando continuar")
    
    # Seleccionar nivel de educación (aleatorio)
    education_options = list(XPATHS["education_options"].values())
    random_education = random.choice(education_options)
    if not bot.click_element(random_education):
        bot.logger.warning("No se pudo seleccionar nivel de educación, intentando continuar")
    
    # Seleccionar signo zodiacal (aleatorio)
    zodiac_options = list(XPATHS["zodiac_options"].values())
    random_zodiac = random.choice(zodiac_options)
    if not bot.click_element(random_zodiac):
        bot.logger.warning("No se pudo seleccionar signo zodiacal, intentando continuar")
    
    # Clic en botón continuar
    if not bot.click_element(XPATHS["button_onboarding_submit"]):
        return False
    
    bot.state['personal_info_selected'] = True
    bot.save_checkpoint()
    
    # Aplicar el delay después de completar este paso
    bot.apply_step_delay()
    
    return True

def select_interests(bot):
    """Módulo: Seleccionar intereses"""
    if bot.state.get('personal_info_selected', False) is False:
        bot.logger.warning("Se debe completar 'select_personal_info' primero")
        return False
        
    bot.logger.info("Iniciando módulo: Seleccionar intereses")
    bot.state['current_module'] = 'select_interests'
    bot.save_checkpoint()
    
    # Seleccionar 5 intereses aleatorios
    interests_options = list(XPATHS["interests"].values())
    selected_interests = random.sample(interests_options, min(5, len(interests_options)))
    
    for interest in selected_interests:
        try:
            if not bot.click_element(interest):
                bot.logger.warning(f"No se pudo seleccionar el interés: {interest}, intentando continuar")
        except Exception as e:
            bot.logger.warning(f"Error al seleccionar interés: {str(e)}")
    
    # Clic en botón continuar
    if not bot.click_element(XPATHS["button_onboarding_submit"]):
        return False
    
    bot.state['interests_selected'] = True
    bot.save_checkpoint()
    
    # Aplicar el delay después de completar este paso
    bot.apply_step_delay()
    
    return True