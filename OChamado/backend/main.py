import os
import functions_framework
from flask import jsonify
from google import genai
from promptia import INSTRUCAO_SISTEMA
# Conexão com a IA (O Google vai pegar a chave das variáveis de ambiente)
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

@functions_framework.http
def chat_ochamado(request):
    # --- TRATAMENTO DE CORS (Obrigatório para o Google) ---
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
        ultima_mensagem = historico_bruto[-1]["content"] if historico_bruto else ""

        conversa_str = " ".join([m["content"].lower() for m in historico_bruto])
        
        if "funcionário" in conversa_str or "funcionario" in conversa_str:
            modo_persona = "\n\n[MODO ATIVO: FUNCIONÁRIO] Use o formato técnico obrigatório."
        elif "cliente" in conversa_str:
            modo_persona = "\n\n[MODO ATIVO: CLIENTE] Responda como FAQ amigável."
        else:
            modo_persona = "\n\n[AVISO]: Pergunte se é Cliente ou Funcionário."

        conhecimento_extra = buscar_conhecimento_extra(ultima_mensagem)

        mensagens_formatadas = []
        for msg in historico_bruto:
            papel = "model" if msg["role"] in ["bot", "assistant"] else "user"
            mensagens_formatadas.append({"role": papel, "parts": [{"text": msg["content"]}]})

        instrucao_final = INSTRUCAO_SISTEMA + modo_persona + conhecimento_extra

        resposta = client.models.generate_content(
            model="gemini-3.1-flash-lite-preview",
            config={"system_instruction": instrucao_final},
            contents=mensagens_formatadas
        )

        resposta = completion.choices[0].message.content
        return (jsonify({"resposta": resposta}), 200, headers)

    except Exception as e:
        print(f"Erro no 3.1 Lite: {str(e)}")
        return (jsonify({"erro": "Erro no motor 3.1 Lite"}), 500, headers)