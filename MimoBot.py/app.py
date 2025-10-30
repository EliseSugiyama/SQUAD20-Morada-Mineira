from flask import Flask, jsonify, request, render_template
import json

# Garante que a pasta ./static seja servida
app = Flask(__name__, static_folder="static", template_folder="templates")

with open("menu.json", "r", encoding="utf-8") as f:
    menu = json.load(f)

cart = []

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/menu", methods=["GET"])
def get_menu():
    return jsonify(menu)

@app.route("/faq/<int:item_id>", methods=["GET"])
def get_faq(item_id):
    item = next((p for p in menu if p["id"] == item_id), None)
    if not item:
        return jsonify({"error": "Produto não encontrado"}), 404
    return jsonify(item.get("faqs", []))

@app.route("/cart", methods=["POST"])
def add_to_cart():
    data = request.json
    item_id = data.get("id")
    options = data.get("options", {})

    item = next((p for p in menu if p["id"] == item_id), None)
    if not item:
        return jsonify({"error": "Produto não encontrado"}), 404

    total = float(item.get("base_price", 0.0))
    if "options" in item:
        for opt_key, choices in options.items():
            for choice in choices:
                opt_list = item["options"].get(opt_key, [])
                opt = next((o for o in opt_list if o["label"] == choice), None)
                if opt:
                    total += float(opt.get("extra", 0.0))

    cart.append({
        "id": item["id"],
        "name": item["name"],
        "selectedOptions": options,
        "total": total
    })
    return jsonify({"message": "Adicionado ao carrinho", "total": total})

@app.route("/cart", methods=["GET"])
def get_cart():
    total_final = sum(float(i["total"]) for i in cart)
    return jsonify({"items": cart, "totalFinal": total_final})

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
        return jsonify({"message": "Item removido do carrinho"})
    else:
        return jsonify({"message": "Item não encontrado no carrinho"}), 404

if __name__ == "__main__":
    app.run(debug=True, port=5000)
