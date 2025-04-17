# modules/profile_setup.py
from config import XPATHS
import time
from appium.webdriver.common.mobileby import MobileBy
from appium import webdriver




def enter_name(bot, first_name):
    """Módulo: Ingresar nombre"""
    bot.logger.info("Iniciando módulo: Ingresar nombre")
    bot.state['current_module'] = 'enter_name'
    bot.save_checkpoint()
    
    # Ingresar el nombre usando el método centralizado
    if not bot.type_text(first_name):
        bot.logger.error("No se pudo ingresar el nombre")
        return False
    
    # Esperar un momento para asegurarse de que se ingresó correctamente
    time.sleep(1)

    
      # Seleccionar hombres
    if not bot.click_element(XPATHS["done_button"]):
        return False
    
    if not bot.click_element(XPATHS["button_onboarding_submit"]):
        return False
    
    if not bot.click_element(XPATHS["lets_go_button"]):
        return False
    
    # Guardar estado
    bot.state['name_entered'] = True
    bot.state['first_name'] = first_name
    bot.save_checkpoint()
    
    # Aplicar el delay después de completar este paso
    bot.apply_step_delay()
    
    return True

def enter_birthday(bot, day):
    """Módulo: Ingresar fecha de nacimiento"""
    if bot.state.get('name_entered', False) is False:
        bot.logger.warning("Se debe completar 'enter_name' primero")
        return False
        
    bot.logger.info("Iniciando módulo: Ingresar fecha de nacimiento")
    bot.state['current_module'] = 'enter_birthday'
    bot.save_checkpoint()
    
    # Ingresar mes
    if not bot.type_text(day):
        bot.logger.error("No se pudo ingresar el mes")
        return False
    
    
    # Esperar un momento para asegurarse de que se ingresó correctamente
    time.sleep(3)
    
    # Clic en botón continuar
    if not bot.click_element(XPATHS["button_onboarding_submit"]):
        return False
    
    bot.state['birthday_entered'] = True
    bot.state['birthday'] = f"{day}"
    bot.save_checkpoint()
    
    # Aplicar el delay después de completar este paso
    bot.apply_step_delay()
    
    return True

def select_gender(bot, show_on_profile=False):
    """Módulo: Seleccionar género"""
    if bot.state.get('birthday_entered', False) is False:
        bot.logger.warning("Se debe completar 'enter_birthday' primero")
        return False
        
    bot.logger.info("Iniciando módulo: Seleccionar género")
    bot.state['current_module'] = 'select_gender'
    bot.save_checkpoint()
    
    # Seleccionar mujer
    if not bot.click_element(XPATHS["woman_button"]):
        return False
    
    # Opcionalmente mostrar en perfil
    if show_on_profile:
        if not bot.click_element(XPATHS["show_gender_checkbox"]):
            return False
    
    # Clic en botón continuar
    if not bot.click_element(XPATHS["agree_button"]):
        return False
    
    bot.state['gender_selected'] = True
    bot.save_checkpoint()
    
    # Aplicar el delay después de completar este paso
    bot.apply_step_delay()
    
    return True

def select_orientation(bot, show_on_profile=False):
    """Módulo: Seleccionar orientación sexual"""
    if bot.state.get('gender_selected', False) is False:
        bot.logger.warning("Se debe completar 'select_gender' primero")
        return False
        
    bot.logger.info("Iniciando módulo: Seleccionar orientación sexual")
    bot.state['current_module'] = 'select_orientation'
    bot.save_checkpoint()
    
    # Seleccionar heterosexual
    if not bot.click_element(XPATHS["straight_button"]):
        return False
    
    # Opcionalmente mostrar en perfil
    if show_on_profile:
        if not bot.click_element(XPATHS["show_sexual_orientation_checkbox"]):
            return False
    
    # Clic en botón continuar
    if not bot.click_element(XPATHS["agree_button"]):
        return False
    
    bot.state['orientation_selected'] = True
    bot.save_checkpoint()
    
    # Aplicar el delay después de completar este paso
    bot.apply_step_delay()
    
    return True

def select_interest(bot):
    """Módulo: Seleccionar interés en hombres"""
    if bot.state.get('orientation_selected', False) is False:
        bot.logger.warning("Se debe completar 'select_orientation' primero")
        return False
        
    bot.logger.info("Iniciando módulo: Seleccionar interés")
    bot.state['current_module'] = 'select_interest'
    bot.save_checkpoint()
    
    # Seleccionar hombres
    if not bot.click_element(XPATHS["men_button"]):
        return False
    
    # Clic en botón continuar
    if not bot.click_element(XPATHS["agree_button"]):
        return False
    
    bot.state['interest_selected'] = True
    bot.save_checkpoint()
    
    # Aplicar el delay después de completar este paso
    bot.apply_step_delay()
    
    return True


def set_distance_preference(bot):
    """Módulo: Configurar preferencia de distancia"""
    if bot.state.get('interest_selected', False) is False:
        bot.logger.warning("Se debe completar 'select_interest' primero")
        return False
        
    bot.logger.info("Iniciando módulo: Configurar preferencia de distancia")
    bot.state['current_module'] = 'set_distance_preference'
    bot.save_checkpoint()
    
    try:
        # Intentar encontrar el slider
        slider_value = None
        try:
            slider_value = bot.driver.find_element(MobileBy.XPATH, XPATHS["distance_slider_value"])
            bot.logger.info("Slider de distancia encontrado")
        except Exception as e:
            bot.logger.warning(f"No se pudo encontrar el valor del slider: {str(e)}")
            
        if slider_value:
            # Obtener la ubicación actual del slider
            location = slider_value.location
            size = slider_value.size
            center_x = location['x'] + size['width'] / 2
            center_y = location['y'] + size['height'] / 2
            
            # Obtener el tamaño de la pantalla
            screen_size = bot.driver.get_window_size()
            
            # Calcular nueva posición (mover un poco a la derecha)
            new_x = min(center_x + 100, screen_size['width'] * 0.8)  # Mover a la derecha pero no demasiado
            
            # Realizar acción de arrastrar
            bot.logger.info(f"Moviendo slider desde ({center_x}, {center_y}) hasta ({new_x}, {center_y})")
            bot.driver.swipe(center_x, center_y, new_x, center_y, 500)  # 500ms de duración del swipe
            
            # Esperar un momento para que la UI se actualice
            time.sleep(1)
        else:
            # Intento alternativo usando la línea del slider
            try:
                slider_line = bot.driver.find_element(MobileBy.XPATH, XPATHS["distance_slider_line"])
                location = slider_line.location
                size = slider_line.size
                
                # Calcular punto para hacer clic (80% del ancho de la línea)
                start_x = location['x']
                width = size['width']
                target_x = start_x + (width * 0.8)
                center_y = location['y'] + size['height'] / 2
                
                # Hacer clic en ese punto
                bot.logger.info(f"Haciendo clic en el punto ({target_x}, {center_y}) de la línea del slider")
                bot.driver.tap([(target_x, center_y)], 100)
                
                # Esperar un momento para que la UI se actualice
                time.sleep(1)
            except Exception as e:
                bot.logger.warning(f"No se pudo encontrar la línea del slider: {str(e)}")
                
                # Si no podemos encontrar ni el valor ni la línea, intentar hacer clic en una posición estimada
                screen_width = bot.driver.get_window_size()['width']
                screen_height = bot.driver.get_window_size()['height']
                
                # Estimar la posición de la barra
                estimated_y = screen_height * 0.5  # Aproximadamente a la mitad de la pantalla
                estimated_x = screen_width * 0.7   # Al 70% hacia la derecha
                
                bot.logger.info(f"Intentando clic estimado en ({estimated_x}, {estimated_y})")
                bot.driver.tap([(estimated_x, estimated_y)], 100)
    except Exception as e:
        bot.logger.error(f"Error al configurar preferencia de distancia: {str(e)}")
    
    # Independientemente de si pudimos mover el slider, intentamos continuar
    time.sleep(1)
    
    # Clic en botón continuar
    if not bot.click_element(XPATHS["button_onboarding_submit"]):
        return False
    
    bot.state['distance_preference_set'] = True
    bot.save_checkpoint()
    
    # Aplicar el delay después de completar este paso
    bot.apply_step_delay()
    
    return True