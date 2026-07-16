from backend.ai.llm_manager import LLMManager
from backend.ai.models_catalog import AITask


def main():

    llm = LLMManager()

    print("=" * 70)
    print("LIA EmployX AI Test")
    print("=" * 70)

    print("\n¿Proveedor conectado?")

    print(llm.is_online())

    print("\nModelos disponibles:")

    print(llm.models())

    print("\nEnviando pregunta...\n")

    respuesta = llm.ask(

        task=AITask.CHAT,

        prompt="Presentate en una sola oración. Eres la IA de LIA EmployX."

    )

    print("=" * 70)

    print(respuesta)

    print("=" * 70)


if __name__ == "__main__":

    main()