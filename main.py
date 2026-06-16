import subprocess
import sys
from pathlib import Path

def run_script(script_path):
    """Ejecuta un script de Python y verifica si terminó con éxito."""
    print(f"\nEjecutando: {script_path}")
    try:
        # Ejecuta el script usando el mismo intérprete de Python actual
        result = subprocess.run([sys.executable, str(script_path)], check=True)
        print(f"{script_path} completado con éxito.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error al ejecutar {script_path}: {e}")
        return False

def main():
    project_root = Path(__file__).resolve().parent
    
    # Definición del pipeline en orden secuencial
    pipeline = [
        project_root / "etapa0_preparacion" / "preparar_dataset.py",
        project_root / "etapa1_mt" / "normalizacion_mt.py",
        project_root / "etapa2_regex" / "etapa2_tokens.py",
        project_root / "etapa3_clasificador" / "clasificador.py",
        project_root / "etapa4_glc" / "gramatica.py",
    ]

    print("-------------------------------------------")
    print("       SpamScanner 2.0 - Pipeline        ")
    print("-------------------------------------------")

    for script in pipeline:
        if not run_script(script):
            print("\nEl pipeline se detuvo debido a un error en una de las etapas.")
            sys.exit(1)

    print("\nTodo el pipeline se ejecutó correctamente.")

if __name__ == "__main__":
    main()
