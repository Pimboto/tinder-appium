# modules/finalize.py
import time
from config import XPATHS

def close_avoid_someone(bot):
    """Módulo: Cerrar ventana de evitar a alguien en Tinder"""
    if bot.state.get('photos_selected', False) is False:
        bot.logger.warning("Se debe completar 'select_photos' primero")
        return False
        
    bot.logger.info("Iniciando módulo: Cerrar ventana de evitar a alguien")
    bot.state['current_module'] = 'close_avoid_someone'
    bot.save_checkpoint()
    
    # Esperar un minuto como se indica
    bot.logger.info("Esperando 60 segundos...")
    time.sleep(60)
    
    # Clic en botón cerrar (X)
    if not bot.click_element(XPATHS["close_button"]):
        bot.logger.warning("No se pudo cerrar la ventana de evitar a alguien, intentando continuar")
    
    bot.state['avoid_someone_closed'] = True
    bot.save_checkpoint()
    
    # Aplicar el delay después de completar este paso
    bot.apply_step_delay()
    
    return True

def decline_notifications(bot):
    """Módulo: Rechazar las notificaciones"""
    if bot.state.get('avoid_someone_closed', False) is False:
        bot.logger.warning("Se debe completar 'close_avoid_someone' primero")
        return False
        
    bot.logger.info("Iniciando módulo: Rechazar notificaciones")
    bot.state['current_module'] = 'decline_notifications'
    bot.save_checkpoint()
    
    # Clic en botón "No quiero"
    if not bot.click_element(XPATHS["no_notifications_button"]):
        bot.logger.warning("No se pudo rechazar las notificaciones, intentando continuar")
    
    bot.state['notifications_declined'] = True
    bot.save_checkpoint()
    
    # Aplicar el delay después de completar este paso
    bot.apply_step_delay()
    
    return True

def complete_tutorial(bot):
    """Módulo: Completar el tutorial de Tinder"""
    if bot.state.get('notifications_declined', False) is False:
        bot.logger.warning("Se debe completar 'decline_notifications' primero")
        return False
        
    bot.logger.info("Iniciando módulo: Completar tutorial")
    bot.state['current_module'] = 'complete_tutorial'
    bot.save_checkpoint()
    
    # Clic en Start tutorial
    if not bot.click_element(XPATHS["start_tutorial_button"]):
        bot.logger.warning("No se pudo iniciar el tutorial, intentando continuar")
    else:
        # Hacer un Like
        if not bot.click_element(XPATHS["like_button"]):
            bot.logger.warning("No se pudo dar Like en el tutorial")
        
        # Hacer un Pass
        if not bot.click_element(XPATHS["pass_button"]):
            bot.logger.warning("No se pudo dar Pass en el tutorial")
        
        # Clic en Let's go
        if not bot.click_element(XPATHS["lets_go_final_button"]):
            bot.logger.warning("No se pudo finalizar el tutorial con Let's go")
    
    bot.state['tutorial_completed'] = True
    bot.save_checkpoint()
    
    # Aplicar el delay después de completar este paso
    bot.apply_step_delay()
    
    return True

    """
    Módulo: Comenzar a deslizar perfiles
    
    Args:
        bot: Instancia de TinderAutomation
        swipes: Número de swipes a realizar
    """
    if bot.state.get('tutorial_completed', False) is False:
        bot.logger.warning("Se debe completar 'complete_tutorial' primero")
        return False
        
    bot.logger.info("Iniciando módulo: Comenzar a deslizar perfiles")
    bot.state['current_module'] = 'start_swiping'
    bot.save_checkpoint()
    
    # Realizar swipes
    likes = 0
    passes = 0
    
    for i in range(swipes):
        # Decidir aleatoriamente si dar Like o Pass
        if random.random() > 0.3:  # 70% probabilidad de Like
            if bot.click_element(XPATHS["like_button"]):
                likes += 1
                bot.logger.info(f"Like #{likes} realizado")
            else:
                bot.logger.warning(f"No se pudo dar Like #{i+1}")
        else:
            if bot.click_element(XPATHS["pass_button"]):
                passes += 1
                bot.logger.info(f"Pass #{passes} realizado")
            else:
                bot.logger.warning(f"No se pudo dar Pass #{i+1}")
        
        # Pequeña pausa entre swipes
        time.sleep(1.5)
    
    bot.state['swipes_completed'] = True
    bot.state['likes_count'] = likes
    bot.state['passes_count'] = passes
    bot.save_checkpoint()
    
    bot.logger.info(f"Swiping completado: {likes} Likes, {passes} Passes")
    
    return True