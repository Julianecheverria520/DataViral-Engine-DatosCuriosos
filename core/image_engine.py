import os

def generar_imagen(prompt, output_path):
    """
    MODO MANUAL: Guarda el prompt en un archivo .txt para usarlo con Gemini.
    """
    prompt_folder = "proyectos/prompts_para_gemini"
    os.makedirs(prompt_folder, exist_ok=True)
    
    # Nombre del archivo basado en el audio/imagen de la escena
    nombre_archivo = os.path.basename(output_path).replace(".jpg", ".txt")
    ruta_txt = os.path.join(prompt_folder, nombre_archivo)
    
    with open(ruta_txt, "w", encoding="utf-8") as f:
        f.write(prompt)
    
    print(f"📝 PROMPT LISTO: {prompt}")
    print(f"📍 Guardado en: {ruta_txt}")
    print("--------------------------------------------------")
    return True