import sys

sys.stdout.reconfigure(encoding='utf-8')

def main(texto, imagen_path=None):
    print(f"Texto recibido: {texto}")
    if imagen_path:
        print(f"Imagen recibida en: {imagen_path}")
        # Aquí puedes procesar la imagen con PIL, cv2, etc.

if __name__ == "__main__":
    texto = sys.argv[1] if len(sys.argv) > 1 else ""
    imagen_path = sys.argv[2] if len(sys.argv) > 2 else None
    main(texto, imagen_path)