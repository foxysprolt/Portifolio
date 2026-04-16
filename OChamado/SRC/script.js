// Removi o import que pode travar o navegador. 
// O cérebro lá no Google já tem o promptia.py dentro dele!

let botao = document.querySelector(".botao-ajuda")
let input = document.querySelector(".caixa-texto")
let chat = document.querySelector("#chat")

// URL do Google Cloud Functions
let urlServidor = "https://southamerica-east1-ochamado-ia.cloudfunctions.net/chat_ochamado"

// Começamos o histórico apenas com a saudação inicial
let historico = [
    {
        role: "assistant",
        content: "Olá! Antes de começarmos, você é um Cliente ou um Funcionário da Power2Go?"
    }
];

window.onload = () => {
    adicionarMensagem("Olá! Antes de começarmos, você é um Cliente ou um Funcionário da Power2Go?", "bot");
};

function adicionarMensagem(texto, tipo) {
    let div = document.createElement("div")
    div.classList.add("msg", tipo)
    div.innerHTML = texto.replace(/\n/g, "<br>")
    chat.appendChild(div)
    chat.scrollTop = chat.scrollHeight
}

async function enviarMensagem() {
    let texto = input.value.trim()
    if (!texto) return

    adicionarMensagem(texto, "user")
    // Adiciona ao histórico local
    historico.push({ role: "user", content: texto }); 
    
    input.value = ""
    adicionarMensagem("Ochamado: analisando...", "bot")

    try {
        const response = await fetch(urlServidor, {
            method: "POST",
            headers: {
                // Aqui é onde o Google exige que esteja perfeito
                "Content-Type": "application/json"
            },
            // Enviamos apenas o histórico de mensagens
            body: JSON.stringify({ historico: historico }) 
        })

        if (!response.ok) {
            // Se der erro, vamos tentar ler o que o Python respondeu
            const erroCorpo = await response.json();
            throw new Error(erroCorpo.erro || "Erro desconhecido");
        }

        let dados = await response.json()
        
        if (chat.lastChild) chat.lastChild.remove();

        let resultado = dados.resposta 
        adicionarMensagem(resultado, "bot")
        historico.push({ role: "assistant", content: resultado });

    } catch (erro) {
        if (chat.lastChild) chat.lastChild.remove();
        adicionarMensagem("Erro: " + erro.message, "bot");
        console.error("Erro detalhado:", erro);
    }
}

botao.addEventListener("click", enviarMensagem)

input.addEventListener("keydown", function(e) {
    if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault()
        enviarMensagem()
    }
})