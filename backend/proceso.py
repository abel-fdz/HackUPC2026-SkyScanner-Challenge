import sys

# MAL: subprocess no verá esto
def principal():
    return "Hola" 

# BIEN: subprocess capturará esto
if __name__ == "__main__":
    print("Hola desde el backend")