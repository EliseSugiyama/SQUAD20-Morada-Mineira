# **SQUAD 20 - Morada Mineira**

Chatbot inteligente para a confeitaria **Morada Mineira** que permite aos clientes navegar pelo cardápio, adicionar itens ao carrinho, obter sugestões personalizadas e finalizar compras via WhatsApp.

### Integrantes: 
- Elise Akie Sugiyama;
- Felippe Cotrim da Silva;
- Heitor Alves Rebouças;
- Henrique Souto de Almeida;
- Hugo da Silva Nunes;
- João Gabriel Lucas Ferreira;
- Júlia Barros Ferraz;
- Marcio Antônio Freitas de Pinho;
- Marcus Vinícius Lima Cardoso Fagundes;

### Mentor:
- Igor Santos;

## Sobre o projeto
A empresa **Morada Mineira** enfrenta dificuldades devido à falta de automação em seus processos de gestão e atendimento ao cliente, o que torna o serviço lento e de difícil administração.  
Como solução, desenvolvemos um **chatbot web** com perguntas pré-programadas e opções de resposta sugeridas, visando agilizar o atendimento e melhorar a experiência do cliente.

## Funcionalidades

- Chat interativo 
- Navegação de cardápio com imagens
- Visualização de favoritos/mais vendidos
- Sugestões personalizadas com desconto em volume
- Carrinho de compras completo
- Integração com WhatsApp para finalização de pedidos

## Utilização

- **Menu**: Clique em "Menu" para ver as categorias e depois escolha os produtos
- **Favoritos**: Clique em "Favoritos" para ver categorias de produtos mais vendidos
- **Sugestões**: Clique em "Sugestões" e forneça: quantidade, tipo de evento, local (ex: "10, casamento, São Paulo")
- **Carrinho**: Clique em "Carrinho" para visualizar e editar seus itens
- **Finalizar**: Complete a compra e envie pelo WhatsApp

## Tecnologias utilizadas

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, JavaScript vanilla
- **Banco de dados**: SQLite
- **Integração**: WhatsApp API

## Estrutura do projeto

```
.
├── app.py                # Servidor Flask e API
├── db.sqlite             # Banco de dados SQLite
├── requirements.txt      # Dependências Python
├── Procfile              # Configuração para deploy
├── README.md             # Este arquivo
├── static/
│   ├── style.css         # Estilos CSS
│   ├── script.js         # Lógica JavaScript
│   └── images/           # Imagens (bot, produtos, fundo)
│       └── MoradaMineira.png
└── templates/
    └── index.html        # Interface principal
```
## Como executar

### Pré-requisitos
- Python 3.7+
- pip

### Instalação Local

1. Clone ou baixe o projeto
2. Abra o PowerShell no diretório do projeto
3. Execute os comandos:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

4. Acesse `http://localhost:5000` no navegador

## Deploy Online

O projeto está pronto para fazer deploy em plataformas como:

### Render.com (Recomendado - Gratuito)
1. Acesse [render.com](https://render.com)
2. Faça login com GitHub
3. Clique "New Web Service"
4. Selecione o repositório
5. Configure:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
6. Clique "Deploy"

### Outras opções
- **Railway.app**: Gratuito com créditos
- **PythonAnywhere**: Plano gratuito disponível

## Licença
Este projeto está licenciado sob a [MIT License](LICENSE).
Este projeto está licenciado sob a [MIT License](LICENSE).
