# cliente HTTP hacia n8n

import requests

N8N_BASE_URL = "http://localhost:5678"


def buscar_vtuber(login: str) -> dict | None:
    try:
        response = requests.get(
            "http://localhost:5678/webhook/vtuber/buscar",
            params={"login": login},
            timeout=5
        )

        #print("STATUS:", response.status_code)
        #print("RAW:", response.text)

        if not response.text.strip():
            print("Respuesta vacía de n8n")
            return None

        payload = response.json()

        if not payload.get("ok"):
            return None

        return payload.get("data")

    except Exception as e:
        print("Error llamando a n8n:", e)
        return None

    
def obtener_vtubers_online() -> list[dict]:
    try:
        response = requests.get(
            f"{N8N_BASE_URL}/webhook/vtuber/online",
            timeout=8
        )
        response.raise_for_status()
        data = response.json()

        if isinstance(data, list):
            return data

        return []

    except Exception as e:
        print("Error llamando a n8n (online):", e)
        return []
   
