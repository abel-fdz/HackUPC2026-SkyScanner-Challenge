# HackUPC2026 - SkyScanner Challenge

## Descripción

Este proyecto es una solución desarrollada para la HackUPC 2026 para SkyScanner. Se trata de un sistema de recomendación de destinos de viaje que combina un sistema experto basado en CLIPS con una interfaz de usuario construida con Streamlit, y que utiliza inteligencia artificial (Gemini) para proporcionar recomendaciones personalizadas.

El sistema permite a los usuarios obtener sugerencias de viajes basadas en preferencias como clima, actividades, presupuesto y otros criterios, integrando datos de hoteles y procesando la información a través de un motor de reglas experto.

## Arquitectura General

El proyecto está dividido en tres componentes principales:

### 1. Sistema Experto CLIPS
- **Ubicación**: Archivos `.clp` en la raíz del proyecto
- **Función**: Motor de regla que procesa las preferencias del usuario y genera recomendaciones de viaje
- **Módulos principales**:
  - `0_main.clp`: Punto de entrada principal que carga todos los módulos
  - `1_ontologia.clp`: Definición de la ontología del dominio
  - `2_instancias.clp`: Instancias de datos (hoteles, destinos, etc.)
  - `3_entrada.clp`: Manejo de entrada de datos
  - `4_abstraccion.clp`: Abstracción de datos
  - `5_heuristica.clp`: Aplicación de heurísticas
  - `6_refinamiento.clp`: Refinamiento de resultados
  - `7_salida.clp`: Formateo de salida

### 2. Backend Python
- **Ubicación**: Carpeta `backend/`
- **Función**: API que integra CLIPS con servicios de IA
- **Archivos principales**:
  - `app.py`: Aplicación principal del backend
  - `clips_bridge.py`: Puente entre Python y CLIPS
  - `instances_generator.py`: Generador de instancias para CLIPS
  - `prompts.py`: Definición de prompts para IA

### 3. Frontend Streamlit
- **Ubicación**: Carpeta `frontend/`
- **Función**: Interfaz de usuario web para interactuar con el sistema
- **Archivos principales**:
  - `app.py`: Aplicación Streamlit principal

## Datos y Recursos

- **Datos de hoteles**: Archivos `.txt` mensuales (abril.txt, maig.txt, etc.) con información de precios de hoteles
- **Scripts de procesamiento**: `hotels_indicative_monthly.py`, `monthly_reader.py` para procesar datos
- **Resultados**: Archivos JSON con resultados procesados
- **CLIPS Runtime**: Carpeta `Clips-6.3/` con el entorno de ejecución de CLIPS
   ```

## Uso

### Ejecutar el Sistema CLIPS
- **Interfaz gráfica**: `make gui`
- **Línea de comandos**: `make cli`
- **Generar dataset**: `make dataset`

### Ejecutar la Aplicación Completa
```bash
streamlit run frontend/app.py
```

### Ejecutar Pruebas
```bash
make test
```

## Estructura del Proyecto

```
HackUPC2026-SkyScanner-Challenge/
├── 0_main.clp                    # Punto de entrada CLIPS
├── 1_ontologia.clp              # Ontología del dominio
├── 2_instancias.clp             # Instancias de datos
├── 3_entrada.clp                # Manejo de entrada
├── 4_abstraccion.clp            # Abstracción de datos
├── 5_heuristica.clp             # Heurísticas
├── 6_refinamiento.clp           # Refinamiento
├── 7_salida.clp                 # Salida
├── dataset.clp                  # Dataset adicional
├── backend/                     # Backend Python
│   ├── app.py
│   ├── clips_bridge.py
│   ├── instances_generator.py
│   └── prompts.py
├── frontend/                    # Frontend Streamlit
│   └── app.py
├── tests/                       # Pruebas
│   ├── run_clips_smoke.py
│   └── output/
├── Clips-6.3/                  # Entorno CLIPS
├── *.txt                        # Datos mensuales de hoteles
├── *.py                         # Scripts de procesamiento
├── requirements.txt             # Dependencias Python
├── Makefile                     # Comandos de automatización
└── README.md                    # Esta documentación
```

## Tecnologías Utilizadas

- **CLIPS**: Sistema experto para lógica de recomendación
- **Python**: Lenguaje principal para backend y procesamiento
- **Streamlit**: Framework para interfaz web
- **Google Gemini**: IA generativa para recomendaciones
- **Clipspy**: Librería Python para integración con CLIPS
