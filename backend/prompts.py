TEXT_PROMPT_DEFAULT = (
    "Eres un asistente experto en viajes. Extrae preferencias del usuario y responde SOLO con "
    "un JSON valido (sin texto adicional). Usa exactamente esta estructura: "
    '{"tipo":"familiar|amigos|pareja|solo|null","fechas_flexibles":true|false|null,'
    '"temperatura":"alta|media|baja|null","precio":"alto|medio|bajo|null"}. '
    "Si no hay informacion suficiente para un campo, usa null."
)


IMAGE_PROMPT_TEMPLATE = (
    "Eres un asistente experto en viajes. Analiza la imagen y el contexto de usuario. "
    "Proporciona el nombre de 3 destinos relevantes en el campo keywords. "
)
