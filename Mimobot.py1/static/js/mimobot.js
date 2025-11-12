// mimobot.js — torna o design interativo (menu, adicionar ao carrinho, chat)

(function () {
  // Seletores confiáveis (baseados no HTML acima)
  const chatColumn = document.querySelector(".chat-scrollbar .flex.flex-col.space-y-6");
  const initialOptionsContainer = document.getElementById("initial-options");
  const sendBtn = document.getElementById("send-btn");
  const input = document.getElementById("chat-input");

  if (!chatColumn) {
    console.error("MimoBot: não encontrou o container de mensagens (.chat-scrollbar .flex.flex-col.space-y-6). Verifique o HTML.");
    return;
  }

  // util: cria e insere mensagem
  function addMessage(text, sender = "bot") {
    const wrapper = document.createElement("div");
    wrapper.className = sender === "user" ? "flex items-end space-x-3 justify-end" : "flex items-end space-x-3";

    if (sender === "bot") {
      wrapper.innerHTML = `
        <img alt="MimoBot" class="h-8 w-8 flex-shrink-0 rounded-full" src="https://lh3.googleusercontent.com/aida-public/AB6AXuA1TB-7hUtSixJCS09gbX4OKJPRRjn96mkc0TbNP0Exdxy2G-FbKyZxDNK_nWIIeZIpZCT2t2Haa2DrTqkU8o5bkVV8WDfRiyaC8fwtrvFhd-MnWfXfr7qNqNkjxUUNd8YChSUdjZQnOszTXKL9KcT6F2ptLuFElgYOnp736f-L1HU8YwgzqyXZVNnS-Sg8GB6HgCA-F77RzpoGQvHO1s3cG7uELcY7FS70VcX6T5E_DfmxmX2BqC6Val7w2rKThC4wilY74XXKobw"/>
        <div class="chat-message-bubble"><div class="rounded-r-lg rounded-tl-lg bg-primary p-4 text-white"><p class="text-sm">${text}</p></div></div>
      `;
    } else {
      // user
      wrapper.innerHTML = `
        <div class="chat-message-bubble"><div class="rounded-l-lg rounded-tr-lg bg-slate-200 p-4 text-slate-800 dark:bg-slate-600 dark:text-slate-100"><p class="text-sm">${text}</p></div></div>
      `;
    }

    chatColumn.appendChild(wrapper);
    // auto-scroll
    wrapper.scrollIntoView({ behavior: "smooth", block: "end" });
  }

  // indicador de typing
  function addTypingIndicator() {
    const el = document.createElement("div");
    el.className = "flex items-end space-x-3 typing-indicator";
    el.innerHTML = `
      <img alt="MimoBot" class="h-8 w-8 flex-shrink-0 rounded-full" src="https://lh3.googleusercontent.com/aida-public/AB6AXuCcajTHUkPnVtNlxTc1d0FwnvWz22xZ6hPUWR84psREb6z31FGgwA--D8KI2C3oYLcrlnkv4rYl7ehOPNN2k_TgyYdQWhJcSSCFsY8-UNKY6HUnfxq7WG3EPaZ7cj8qmjjKQX_Ye23JdR-hA4Jp6cH1On2d08nYJUdUlmhA9ejB2e496XSwg_tbPliX1gA3Bv6SknM_VBPYCSGk3IBrZfucbwUEF9Vd4r7_PoAIisSaxPHKJvLFSa5x3EmHphvgumPk37BO-RQSgfA"/>
      <div class="chat-message-bubble"><div class="rounded-r-lg rounded-tl-lg bg-primary p-4 text-white">
        <div class="flex items-center space-x-1.5">
          <span class="h-2 w-2 animate-pulse rounded-full bg-white/50"></span>
          <span class="h-2 w-2 animate-pulse rounded-full bg-white/50"></span>
          <span class="h-2 w-2 animate-pulse rounded-full bg-white/50"></span>
        </div>
      </div></div>
    `;
    chatColumn.appendChild(el);
    el.scrollIntoView({ behavior: "smooth", block: "end" });
    return el;
  }

  // fetch /chat para respostas textuais simples
  async function askChatBackend(message) {
    const res = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message })
    });
    return await res.json();
  }

  // fetch /menu e mostra botões clicáveis dos produtos
  async function showMenu() {
    addMessage("Buscando o menu... ☕️");
    const typing = addTypingIndicator();
    try {
      const res = await fetch("/menu");
      const menu = await res.json();
      typing.remove();

      addMessage("Aqui estão nossos produtos:");
      // criar botões para cada produto
      const container = document.createElement("div");
      container.className = "flex flex-col space-y-2 w-full max-w-[calc(75%-12px)]";

      menu.forEach(item => {
        const btn = document.createElement("button");
        btn.className = "w-full rounded-lg bg-orange-100 p-3 text-left font-medium text-orange-800 transition hover:bg-orange-200 dark:bg-slate-700 dark:text-orange-300 dark:hover:bg-slate-600";
        btn.textContent = `${item.name} — R$${Number(item.base_price).toFixed(2)}`;
        btn.onclick = async () => {
          addMessage(`${item.name} — R$${Number(item.base_price).toFixed(2)}`, "user");
          await addToCart(item.id);
        };
        container.appendChild(btn);
      });

      chatColumn.appendChild(container);
      container.scrollIntoView({ behavior: "smooth", block: "end" });

    } catch (err) {
      console.error(err);
      typing.remove();
      addMessage("Erro ao carregar o menu. Tente novamente.");
    }
  }

  // adiciona ao carrinho via POST /cart e mostra o total atual
  async function addToCart(id) {
    const typing = addTypingIndicator();
    try {
      const res = await fetch("/cart", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id })
      });
      const data = await res.json();
      typing.remove();

      if (res.ok) {
        addMessage(`✅ ${data.message} (R$${Number(data.total).toFixed(2)})`);
        await showCartSummary(); // mostra resumo
      } else {
        addMessage(data.error || "Erro ao adicionar ao carrinho.");
      }
    } catch (err) {
      typing.remove();
      console.error(err);
      addMessage("Erro de conexão ao adicionar ao carrinho.");
    }
  }

  // mostra resumo do carrinho via GET /cart
  async function showCartSummary() {
    try {
      const res = await fetch("/cart");
      const data = await res.json();
      const items = data.items || [];
      let text = `🛒 Carrinho: ${items.length} item(s) — Total: R$${Number(data.totalFinal).toFixed(2)}`;
      addMessage(text);
    } catch (err) {
      console.error(err);
      addMessage("Não foi possível obter o carrinho.");
    }
  }

  // handler para os botões iniciais (conhecer, encomendar, dúvidas, B2B)
  function attachInitialButtons() {
    const buttons = document.querySelectorAll(".initial-btn");
    buttons.forEach(btn => {
      btn.addEventListener("click", async (e) => {
        const txt = btn.textContent.trim();
        addMessage(txt, "user");

        if (txt.toLowerCase().includes("conhecer")) {
          addMessage("A Morada Mineira é uma confeitaria artesanal com sabores de Minas ❤️");
        } else if (txt.toLowerCase().includes("encomendar")) {
          await showMenu();
        } else if (txt.toLowerCase().includes("dúvidas") || txt.toLowerCase().includes("duvidas")) {
          addMessage("Pergunte sobre: produtos, prazos de entrega ou formas de pagamento.");
        } else if (txt.toLowerCase().includes("b2b")) {
          addMessage("Para B2B, entre em contato: comercial@moradamineira.com");
        }
      });
    });
  }

  // botão enviar e Enter do input
  sendBtn.addEventListener("click", async () => {
    const text = input.value.trim();
    if (!text) return;
    addMessage(text, "user");
    input.value = "";

    // se for palavra menu, abrir menu (melhor UX)
    if (text.toLowerCase().includes("menu") || text.toLowerCase().includes("cardapio") || text.toLowerCase().includes("cardápio")) {
      await showMenu();
      return;
    }

    const typing = addTypingIndicator();
    try {
      const res = await askChatBackend(text);
      typing.remove();
      if (res && res.response) addMessage(res.response);
      else addMessage("Ops — sem resposta do servidor.");
    } catch (err) {
      typing.remove();
      console.error(err);
      addMessage("Erro ao conectar com o servidor.");
    }
  });

  input.addEventListener("keypress", (e) => {
    if (e.key === "Enter") sendBtn.click();
  });

  // inicializações
  attachInitialButtons();
  // opcional: mensagem de boas-vindas (já existe no HTML estático, então não repete)
})();
