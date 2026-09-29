from app.services.ai_client import ask_ai

ASSISTANT_SYSTEM_PROMPT = (
    "Eres el asistente virtual de PetCloud, una tienda en línea de productos "
    "para mascotas. Responde de forma breve, amable y útil sobre productos, "
    "pedidos o cuidado de mascotas. Si no sabes algo específico del negocio, "
    "dilo con honestidad en vez de inventar datos."
)


def get_assistant_reply(message: str) -> str:
    return ask_ai(ASSISTANT_SYSTEM_PROMPT, message)


def get_recommendations(customer_name: str, recent_categories: list[str]) -> str:
    categories_text = ", ".join(recent_categories) if recent_categories else "ninguna categoría reciente"
    prompt = (
        f"El cliente {customer_name} ha comprado recientemente productos de: {categories_text}. "
        "Sugiere 3 productos o categorías relacionadas que le podrían interesar, "
        "en una lista corta, sin explicaciones largas."
    )
    return ask_ai(ASSISTANT_SYSTEM_PROMPT, prompt)
