from flask import Flask, render_template, request, jsonify
import json
from pathlib import Path

app = Flask(__name__, static_folder="static", template_folder="templates")

MENU_PATH = Path(__file__).parent / "menu.json"

# helper para ler menu
def load_menu():
    try:
        with open(MENU_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

# carrinho simples em memória
cart = []

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/menu", methods=["GET"])
def get_menu():
    return jsonify(load_menu())

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json or {}
    text = (data.get("message") or "").strip().lower()

    if not text:
        return jsonify({"response": "Pode me dizer o que deseja?"})

    # respostas simples. você pode adaptar para lógica mais complexa
    if any(w in text for w in ["oi", "olá", "ola", "bom dia", "boa tarde"]):
        r = "Oi 👋! Eu sou o MimoBot — como posso te ajudar hoje?"
    elif "menu" in text or "cardápio" in text or "cardapio" in text:
        r = "Claro! Vou mostrar o menu para você. 👇"
    elif "encomendar" in text or "pedido" in text:
        r = "Perfeito! Diga qual produto do menu você quer ou clique no produto diretamente."
    else:
        r = "Desculpe, ainda estou aprendendo. Tente 'menu' ou 'encomendar'."

    return jsonify({"response": r})

# CART endpoints
@app.route("/cart", methods=["GET"])
def get_cart():
    total = sum(float(i["total"]) for i in cart)
    return jsonify({"items": cart, "totalFinal": total})

@app.route("/cart", methods=["POST"])
def add_to_cart():
    data = request.json or {}
    item_id = data.get("id")
    menu = load_menu()
    item = next((p for p in menu if p.get("id") == item_id), None)
    if not item:
        return jsonify({"error": "Produto não encontrado"}), 404

    total = float(item.get("base_price", 0.0))
    cart.append({"id": item["id"], "name": item["name"], "total": total})
    return jsonify({"message": "Adicionado ao carrinho", "total": total})

@app.route("/cart", methods=["DELETE"])
def clear_cart():
    global cart
    cart = []
    return jsonify({"message": "Carrinho limpo"})

@app.route("/cart/<int:item_id>", methods=["DELETE"])
def remove_from_cart(item_id):
    global cart
    before = len(cart)
    cart = [i for i in cart if i["id"] != item_id]
    if len(cart) < before:
        return jsonify({"message": "Item removido"})
    return jsonify({"message": "Item não encontrado"}), 404

if __name__ == "__main__":
    app.run(debug=True, port=5000)
