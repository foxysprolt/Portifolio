import os
import functions_framework
from flask import jsonify
from groq import Groq

# Inicializa o cliente da Groq
# Você vai passar a chave no comando de deploy
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def obter_instrucoes():
    """Lê as instruções do seu arquivo promptia.py"""
    caminho = os.path.join(os.path.dirname(__file__), 'promptia.py')
    if os.path.exists(caminho):
        try:
            with open(caminho, 'r', encoding='utf-8') as f:
                conteudo = f.read()
                # Limpa sujeira de código se houver
                return conteudo.replace('INSTRUCAO_SISTEMA =', '').replace('"""', '').strip()
        except:
            pass
    return "Você é o Ochamado, especialista da Power2Go."

@functions_framework.http
def chat_ochamado(request):
    # CORS
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST',
            'Access-Control-Allow-Headers': 'Content-Type',
        }
        return ('', 204, headers)

    headers = {'Access-Control-Allow-Origin': '*'}

    try:
        dados = request.get_json()
        if not dados or 'historico' not in dados:
            return (jsonify({"erro": "Sem histórico"}), 400, headers)

        historico_bruto = dados.get("historico", [])
        instrucao_sistema = obter_instrucoes()

        # Formata as mensagens para a Groq
        mensagens = [{"role": "system", "content": instrucao_sistema}]
        
        for msg in historico_bruto:
            if msg.get("role") == "system": continue
            # Groq aceita 'user' e 'assistant'
            papel = "assistant" if msg.get("role") in ["bot", "assistant", "model"] else "user"
            mensagens.append({"role": papel, "content": msg.get("content", "")})

        # Chamada para o Llama 3 (Groq)
        # Esse modelo llama3-70b-8192 é comparável ao Gemini 1.5 Pro
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=mensagens,
            temperature=0.7,
            max_tokens=2048
        )

        resposta = completion.choices[0].message.content
        return (jsonify({"resposta": resposta}), 200, headers)

    except Exception as e:
        return (jsonify({"erro": str(e)}), 500, headers)