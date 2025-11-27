from flask import Flask, request, jsonify, render_template, redirect
import sqlite3
import os
import json
from urllib.parse import quote_plus
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'db.sqlite')

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-change-me'

COMPANY_WHATSAPP_NUMBER = '5561996393007' 
COMPANY_WEBSITE = 'https://www.moradamineira.com.br'

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    created = False
    if not os.path.exists(DB_PATH):
        created = True
    conn = get_db()
    cur = conn.cursor()
    
    cur.executescript('''
    CREATE TABLE IF NOT EXISTS menu_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT,
        name TEXT NOT NULL,
        base_price REAL NOT NULL,
        description TEXT,
        picture_url TEXT,
        bestseller INTEGER DEFAULT 0
    );

    CREATE TABLE IF NOT EXISTS option_groups (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        menu_item_id INTEGER NOT NULL,
        `key` TEXT NOT NULL,
        type TEXT NOT NULL DEFAULT 'single',
        FOREIGN KEY(menu_item_id) REFERENCES menu_items(id)
    );

    CREATE TABLE IF NOT EXISTS options (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        menu_item_id INTEGER NOT NULL,
        option_group_id INTEGER,
        name TEXT NOT NULL,
        price_modifier REAL DEFAULT 0.0,
        FOREIGN KEY(menu_item_id) REFERENCES menu_items(id),
        FOREIGN KEY(option_group_id) REFERENCES option_groups(id)
    );

    CREATE TABLE IF NOT EXISTS best_sellers (
        menu_item_id INTEGER PRIMARY KEY,
        count INTEGER DEFAULT 0,
        FOREIGN KEY(menu_item_id) REFERENCES menu_items(id)
    );

    CREATE TABLE IF NOT EXISTS carts (
        id TEXT PRIMARY KEY,
        created_at TEXT
    );

    CREATE TABLE IF NOT EXISTS cart_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cart_id TEXT,
        menu_item_id INTEGER,
        selected_options TEXT,
        quantity INTEGER,
        unit_price REAL,
        FOREIGN KEY(cart_id) REFERENCES carts(id),
        FOREIGN KEY(menu_item_id) REFERENCES menu_items(id)
    );
    ''')
    conn.commit()

    cur.execute('SELECT COUNT(1) as cnt FROM menu_items')
    cnt = 0
    try:
        cnt = cur.fetchone()['cnt']
    except Exception:
        cnt = 0
    if cnt == 0:
        seed_sample_data(conn)

    conn.close()

def seed_sample_data(conn):
    cur = conn.cursor()
    
    provided = [
    {
    "id": 1,
    "category": "Tortas Especialidades",
    "name": "Marta Rocha",
    "description": "A melhor Marta Rocha do mundo! Resultado de muita pesquisa, dedicação e amor da nossa Chef Confeiteira. Baba de moça, suspiros, praliné de castanha de caju e nozes no pão de ló branco, coberto com muito suspiro. E que suspiro!",
    "image": "/static/images/MartaRocha.jpg",
    "base_price": 0.00,
    "bestseller": True,
    "options": {
      "tamanho": [
        { "label": "1.0 kg", "extra": 98.00 },
        { "label": "1.5 kg", "extra": 147.00 },
        { "label": "2.0 kg", "extra": 196.00 },
        { "label": "3.0 kg", "extra": 294.00 }
      ], 
      "type": "single"
    },
  },

  {
    "id": 2,
    "category": "Tortas Especialidades",
    "name": "Cascata de Morango",
    "description": "Recheio de creme de brigadeiro com morangos frescos. Cobertura de morangos frescos, geleia de morango e chocolate. Pão de ló chocolate.Recheio de creme de brigadeiro com morangos frescos. Cobertura de morangos frescos, geleia de morango e chocolate. Pão de ló chocolate.",
    "image": "/static/images/PlaceHolder.jpg",
    "base_price": 0.00,
    "bestseller": True,
    "options": {
      "tamanho": [
        { "label": "1.5 kg", "extra": 178.49 },
        { "label": "2.0 kg", "extra": 238.00 },
        { "label": "2.5 kg", "extra": 297.50 },
        { "label": "3.0 kg", "extra": 357.00 }
      ], 
      "type": "single"
    },
  },

  {
    "id": 3,
    "category": "Tortas Especialidades",
    "name": "Morango Espelhada",
    "description": "Recheio de baba de moça, chantilly, geleia de morango e suspiro. Cobertura de morangos frescos e geleia de morango. Pão de ló branco.",
    "image": "/static/images/PlaceHolder.jpg",
    "base_price": 0.00,
    "bestseller": False,
    "options": {
      "tamanho": [
        { "label": "1.5 kg", "extra": 163.50 },
        { "label": "2.0 kg", "extra": 218.00 },
        { "label": "3.0 kg", "extra": 327.00 }
      ], 
      "type": "single"
    },
  },

  {
    "id": 4,
    "category": "Tortas Especialidades",
    "name": "Bia",
    "description": "Leve, deliciosa e bela são algumas das qualidades dessa torta que todos já conhecem pelo nome. Baba de moça, morangos frescos e pão de ló branco, coberto com morangos, geleia de morango, suspiro e chantilly.Leve, deliciosa e bela são algumas das qualidades dessa torta que todos já conhecem pelo nome. Baba de moça, morangos frescos e pão de ló branco, coberto com morangos, geleia de morango, suspiro e chantilly.",
    "image": "/static/images/PlaceHolder.jpg",
    "base_price": 0.00,
    "bestseller": False,
    "options": {
      "tamanho": [
        { "label": "1.3 kg", "extra": 141.70 },
        { "label": "2.0 kg", "extra": 218.00 },
        { "label": "3.0 kg", "extra": 327.00 }
      ], 
      "type": "single"
    },
  },

  {
    "id": 5,
    "category": "Tortas Especialidades",
    "name": "Extravagance",
    "description": "Uma combinação de dar água na boca. Creme de chocolate trufado, baba de moça, morangos frescos, no pão de ló de chocolate, coberto com ganache e muitas frutas vermelhas.",
    "image": "/static/images/Extravagance.jpg",
    "base_price": 0.00,
    "bestseller": False,
    "options": {
      "tamanho": [
        { "label": "1.5 kg", "extra": 208.50 },
        { "label": "2.0 kg", "extra": 278.00 },
        { "label": "3.0 kg", "extra": 417.00 }
      ], 
      "type": "single"
    },
  },

  {
    "id": 6,
    "category": "Tortas Especialidades",
    "name": "Sublime",
    "description": "Baba de moça, creme trufado de chocolate branco, variegato de amarena e mousse de chocolate branco. Pão de ló branco. Cobertura chantilly e detalhes em ganache de chocolate branco.",
    "image": "/static/images/Sublime.jpg",
    "base_price": 0.00,
    "bestseller": False,
    "options": {
      "tamanho": [
        { "label": "1.0 kg", "extra": 119.00 },
        { "label": "1.5 kg", "extra": 178.50 },
        { "label": "2.0 kg", "extra": 238.00 },
        { "label": "3.0 kg", "extra": 357.00 }
      ], 
      "type": "single"
    },
  },

  {
    "id": 7,
    "category": "Tortas",
    "name": "Baba de Moça",
    "description": "Recheio baba de moça. Cobertura de chantilly. Massa de pão de ló branco.",
    "image": "/static/images/BabaMoca.jpg",
    "base_price": 0.00,
    "bestseller": True,
    "options": {
      "tamanho": [
        { "label": "1.0 kg", "extra": 94.00 },
        { "label": "1.5 kg", "extra": 141.00 },
        { "label": "2.0 kg", "extra": 188.00 },
        { "label": "3.0 kg", "extra": 282.00 }
      ], 
      "type": "single"
    }
  },

  {
    "id": 8,
    "category": "Tortas",
    "name": "Baba de Moça com Abacaxi",
    "description": "Recheio Baba de moça e creme de abacaxi. Cobertura de marshmallow mesclado. Massa de pão de ló branco.",
    "image": "/static/images/BabaMocaAbacaxi.jpg",
    "base_price": 0.00,
    "bestseller": True,
    "options": {
      "tamanho": [
        { "label": "1.0 kg", "extra": 94.00 },
        { "label": "1.5 kg", "extra": 141.00 },
        { "label": "2.0 kg", "extra": 188.00 },
        { "label": "3.0 kg", "extra": 282.00 }
      ], 
      "type": "single"
    }
  },
  
  {
    "id": 9,
    "category": "Tortas",
    "name": "Amor Perfeito",
    "description": "Recheio de creme de coco, creme de brigadeiro e mousse de chocolate. Cobertura de Ganache, brigadeiro e beijinho de coco. Massa de pão de ló de chocolate.",
    "image": "/static/images/AmorPerfeito.jpg",
    "base_price": 0.00,
    "bestseller": False,
    "options": {
      "tamanho": [
        { "label": "1.0 kg", "extra": 95.00 },
        { "label": "1.5 kg", "extra": 142.50 },
        { "label": "2.0 kg", "extra": 190.00 },
        { "label": "3.0 kg", "extra": 285.00 }
      ], 
      "type": "single"
    }
  },

  {
    "id": 10,
    "category": "Tortas",
    "name": "Torta de Brigadeiro",
    "description": "Recheio de creme de brigadeiro. Cobertura de creme trufado de chocolate meio amargo, chocolate granulado e brigadeiros. Massa de pão de ló de chocolate.",
    "image": "/static/images/TortaBrigadeiro.jpg",
    "base_price": 0.00,
    "bestseller": True,
    "options": {
      "tamanho": [
        { "label": "1.0 kg", "extra": 94.00 },
        { "label": "1.5 kg", "extra": 141.00 },
        { "label": "2.0 kg", "extra": 188.00 },
        { "label": "3.0 kg", "extra": 282.00 }
      ], 
      "type": "single"
    }
  },

  {
    "id": 11,
    "category": "Tortas",
    "name": "Floresta Negra",
    "description": "Recheio de chantilly com cereja. Cobertura de chantilly, chocolate em raspas e cerejas. Massa pão de ló de chocolate.",
    "image": "/static/images/FlorestaNegra.jpg",
    "base_price": 0.00,
    "bestseller": True,
    "options": {
      "tamanho": [
        { "label": "1.0 kg", "extra": 94.00 },
        { "label": "1.5 kg", "extra": 141.00 },
        { "label": "2.0 kg", "extra": 188.00 },
        { "label": "3.0 kg", "extra": 282.00 }
      ], 
      "type": "single"
    }
  },

  {
    "id": 12,
    "category": "Tortas",
    "name": "Torta de Limão",
    "description": "Recheio de creme de limão, chantilly e suspiros. Cobertura de chantilly e creme de limão. Massa pão de ló.",
    "image": "/static/images/TortaLimao.jpg",
    "base_price": 0.00,
    "bestseller": False,
    "options": {
      "tamanho": [
        { "label": "1.0 kg", "extra": 94.00 },
        { "label": "1.5 kg", "extra": 141.00 },
        { "label": "2.0 kg", "extra": 188.00 },
        { "label": "3.0 kg", "extra": 282.00 }
      ], 
      "type": "single"
    }
  },

  {
    "id": 13,
    "category": "Tortas",
    "name": "Torta de Nozes",
    "description": "Recheio de creme de nozes, creme trufado de chocolate meio amargo e praliné de castanha do caju. Cobertura de creme ganache e nozes. Massa pão de ló de chocolate.",
    "image": "/static/images/PlaceHolder.jpg",
    "base_price": 0.00,
    "bestseller": False,
    "options": {
      "tamanho": [
        { "label": "1.0 kg", "extra": 119.00 },
        { "label": "1.5 kg", "extra": 178.50 },
        { "label": "2.0 kg", "extra": 238.00 },
        { "label": "3.0 kg", "extra": 357.00 }
      ], 
      "type": "single"
    }
  },

  {
    "id": 14,
    "category": "Tortas",
    "name": "Torta prestígio mesclada",
    "description": "Recheio de creme de coco. Cobertura de marshmallow mesclado com calda de chocolate. Massa pão de ló de chocolate.",
    "image": "/static/images/PrestigioMesclada.jpg",
    "base_price": 00.00,
    "bestseller": True,
    "options": {
      "tamanho": [
        { "label": "1.0 kg", "extra": 94.00 },
        { "label": "1.5 kg", "extra": 141.00 },
        { "label": "2.0 kg", "extra": 188.00 },
        { "label": "3.0 kg", "extra": 282.00 }
      ], 
      "type": "single"
    }
  },

  {
    "id": 15,
    "category": "Tortas",
    "name": "Torta Brigadeiro com Mousse",
    "description": "Recheio de creme de brigadeiro com mousse de chocolate. Cobertura de mousse de chocolate, creme trufado e creme de brigadeiro. Massa pão de ló de chocolate.",
    "image": "/static/images/BrigadeiroMousse.jpg",
    "base_price": 0.00,
    "bestseller": False,
    "options": {
      "tamanho": [
        { "label": "1.0 kg", "extra": 94.00 },
        { "label": "1.5 kg", "extra": 141.00 },
        { "label": "2.0 kg", "extra": 188.00 },
        { "label": "3.0 kg", "extra": 282.00 }
      ], 
      "type": "single"
    }
  },

  {
    "id": 16,
    "category": "Tortas",
    "name": "Massa amanteigada, creme de limão e merengue.",
    "description": "Massa amanteigada, creme de limão e merengue.",
    "image": "/static/images/MerengueLimao.jpg",
    "base_price": 0.00,
    "bestseller": False,
    "options": {
      "tamanho": [
        { "label": "1.0 kg", "extra": 92.00 },
        { "label": "1.5 kg", "extra": 138.00 }
      ], 
      "type": "single"
    }
  },

  {
    "id": 17,
    "category": "Tortas",
    "name": "Lia",
    "description": "Recheio baba de moça, creme de ameixa e creme de abacaxi. Cobertura: chantilly. Massa: pão de ló.",
    "image": "/static/images/PlaceHolder.jpg",
    "base_price": 0.00,
    "bestseller": False,
    "options": {
      "tamanho": [
        { "label": "1.0 kg", "extra": 94.00 },
        { "label": "1.5 kg", "extra": 141.00 },
        { "label": "2.0 kg", "extra": 188.00 },
        { "label": "3.0 kg", "extra": 282.00 }
      ], 
      "type": "single"
    }
  },

  {
    "id": 18,
    "category": "Tortas",
    "name": "Torta Ninho com Frutas do Bosque",
    "description": "R: Creme de ninho e variegato de frutas do bosque C:Chantilly e leite em pó c/ frutas do bosque M: Pão de ló branco",
    "image": "/static/images/TortaNinhoBosque.jpg",
    "base_price": 0.00,
    "bestseller": True,
    "options": {
      "tamanho": [
        { "label": "1.0 kg", "extra": 95.00 },
        { "label": "1.5 kg", "extra": 142.50 },
        { "label": "2.0 kg", "extra": 190.00 },
        { "label": "3.0 kg", "extra": 285.00 }
      ], 
      "type": "single"
    }
  },

  {
    "id": 19,
    "category": "Bolos",
    "name": "Bolo inteiro",
    "description": "10 fantásticas opções de recheios de bolo!",
    "image": "/static/images/PlaceHolder.jpg",
    "base_price": 0.00,
    "bestseller": True,
    "options": {
      "sabores": [
        { "label": "Bolo de mandioca (1kg)", "extra": 42.00 },
        { "label": "Bolo de banana com canela (1kg)", "extra": 42.00 },
        { "label": "Bolo de cenoura (1kg)", "extra": 44.00 },
        { "label": "Bolo de milho (1kg)", "extra": 48.00 },
        { "label": "Bolo de chocolate (1kg)", "extra": 41.00 },
        { "label": "Bolo de milho com coco (1kg)", "extra": 48.00 },
        { "label": "Bolo de coco (1kg)", "extra": 41.00 },
        { "label": "Bolo mármore (1kg)", "extra": 41.00 },
        { "label": "Bolo de laranja (1kg)", "extra": 41.00 },
        { "label": "Bolo de milho caseiro (1kg)", "extra": 56.00 }
      ], 
      "type": "multiple"
    }
  }, 

  {
    "id": 20,
    "category": "Doces",
    "name": "Bombons",
    "description": "Bombom é um doce constituído basicamente por um recheio e recoberto por uma camada de chocolate ou glacê. Foto ilustrativa. Os bombons são vendidos em forminhas brancas simples.",
    "image": "/static/images/Bombons.jpg",
    "base_price": 0.00,
    "bestseller": False,
    "options": {
      "sabores": [
        { "label": "Ameixa (25 un)", "extra": 65.00 },
        { "label": "Cereja (25 un)", "extra": 70.00 },
        { "label": "Coco (25 un)", "extra": 65.00 },
        { "label": "Passas (25 un)", "extra": 65.00 },
        { "label": "Uva (25 un)", "extra": 70.00 },
        { "label": "Castanha de caju (25 un)", "extra": 70.00 },
        { "label": "Nozes (25 un)", "extra": 70.00 }
      ], 
      "type": "multiple"
    }
  },

  {
    "id": 21,
    "category": "Doces",
    "name": "Docinhos",
    "description": "Pequeno doce confeitado, servido em fôrmas de papel.",
    "image": "/static/images/Docinhos.jpg",
    "base_price": 0.00,
    "bestseller": True,
    "options": {
      "sabores": [
        { "label": "Brigadeiro (25 un)", "extra": 26.25 },
        { "label": "Beijinho de Coco (25 un)", "extra": 26.25 },
        { "label": "Beijinho de Leite Ninho (25 un)", "extra": 31.50 },
        { "label": "Olho de Sogra (25 un)", "extra": 26.25 },
        { "label": "Cajuzinho (25 un)", "extra": 26.25 },
        { "label": "Casadinho (25 un)", "extra": 31.50 },
        { "label": "Croissant de Banana (25 un)", "extra": 32.25 },
        { "label": "Croissant de Goiaba", "extra": 34.75 },
        { "label": "Croissant de Maça (25 un)", "extra": 32.25 },
        { "label": "Tartelette de Morango (25 un)", "extra": 38.50 },
        { "label": "Tartelette de Limão (25 un)", "extra": 38.50 },
        { "label": "Tartelette de Nozes (25 un)", "extra": 42.25 },
        { "label": "Tartelette de Sonho de Valsa (25 un)", "extra": 38.50 },
        { "label": "Bombinhas de Chocolate (25 un)", "extra": 40.00 },
        { "label": "Bombinhas de Creme (25 un)", "extra": 40.00 },
        { "label": "Quindim (25 un)", "extra": 40.00 },
        { "label": "Mini Churros (25 un)", "extra": 25.00 }
      ], 
      "type": "multiple"
    }
  },

  {
    "id": 22,
    "category": "Doces",
    "name": "Pudim",
    "description": "Pequeno doce confeitado, servido em fôrmas de papel.",
    "image": "/static/images/PlaceHolder.jpg",
    "base_price": 0.00,
    "bestseller": True,
    "options": {
      "sabores": [
        { "label": "Pudim Grande", "extra": 120.00 }
      ], 
      "type": "single"
    }
  },

  {
    "id": 23,
    "category": "Salgados",
    "name": "Tortas Salgadas",
    "description": "Deliciosas tortas salgadas em diversos sabores.",
    "image": "/static/images/TortasSalgadas.jpg",
    "base_price": 0.00,
    "bestseller": False,
    "options": {
      "sabores": [
        { "label": "Legumes (1 kg)", "extra": 89.00 },
        { "label": "Empadão de Frango (1 kg)", "extra": 99.00 },
        { "label": "Empadão de Franco com Catupiry (1 kg)", "extra": 99.00 },
        { "label": "Empadão de Palmito (1 kg)", "extra": 99.00 },
        { "label": "Empadão de Camarão (1 kg)", "extra": 109.00 }
      ], 
      "type": "multiple"
    }
  },

  {
    "id": 24,
    "category": "Salgados",
    "name": "Salgados Fritos",
    "description": "Para comprar um cento (100 un), basta selecionar o mesmo sabor 4 vezes.",
    "image": "/static/images/SalgadosFritos.jpg",
    "base_price": 0.00,
    "bestseller": True,
    "options": {
      "sabores": [
        { "label": "Coxinha de Frango (25 un)", "extra": 22.00 },
        { "label": "Coxinha de Frango com Catupiry (25 un)", "extra": 24.00 },
        { "label": "Risole de Carne (25 un)", "extra": 24.75 },
        { "label": "Risole de Milho (25 un)", "extra": 21.00 },
        { "label": "Risole de Queijo (25 un)", "extra": 24.75 },
        { "label": "Risole Napolitano (25 un)", "extra": 24.75 },
        { "label": "Enroladinho de Salsicha (25 un)", "extra": 19.75 },
        { "label": "Quibe (25 un)", "extra": 24.75 },
        { "label": "Quibe com Catupiry (25 un)", "extra": 24.75 },
        { "label": "Maravilha de Queijo (25 un)", "extra": 27.25 },
        { "label": "Croquete de Carne (25 un)", "extra": 21.00 },
        { "label": "Croquete de Carne com Provolone (25 un)", "extra": 29.00 },
        { "label": "Croquete de Frango (25 un)", "extra": 21.00 },
        { "label": "Croquete de Bacalhau (25 un)", "extra": 39.75 }
      ], 
      "type": "multiple"
    }
  },

  {
    "id": 25,
    "category": "Salgados",
    "name": "Salgados Assados",
    "description": "Para comprar um cento (100 un), basta selecionar o mesmo sabor 4 vezes.",
    "image": "/static/images/SalgadosAssados.jpg",
    "base_price": 0.00,
    "bestseller": True,
    "options": {
      "sabores": [
        { "label": "Enroladinho de Salsicha Assado (25 un)", "extra": 22.25 },
        { "label": "Enroladinho de Queijo (25 un)", "extra": 31.50 },
        { "label": "Esfiha de Carne (25 un)", "extra": 31.50 },
        { "label": "Esfiha de Frango (25 un)", "extra": 24.75 },
        { "label": "Pão Pizza (25 un)", "extra": 31.50 },
        { "label": "Pão da Vovó (25 un)", "extra": 31.50 },
        { "label": "Empanada de Frango (25 un)", "extra": 24.75 },
        { "label": "Empanada de Camarão (25 un)", "extra": 29.75 },
        { "label": "Empanada de Palmito (25 un)", "extra": 27.25 },
        { "label": "Pastel Assado de Presunto (25 un)", "extra": 29.75 },
        { "label": "Pastel Assado de Frango (25 un)", "extra": 29.75 },
        { "label": "Croissant de Frango (25 un)", "extra": 32.25 },
        { "label": "Croissant de Presunto (25 un)", "extra": 32.25 },
        { "label": "Folhado de Frango (25 un)", "extra": 32.25 },
        { "label": "Folhado de Presunto (25 un)", "extra": 32.25 },
        { "label": "Folhado de Queijo (25 un)", "extra": 29.75 },
        { "label": "Folhado de Bacon com Fios de Ovos (25 un)", "extra": 34.75 },
        { "label": "Folhado de Bacom com Ameixa (25 un)", "extra": 34.75 },
        { "label": "Tartelette de Frango com Azeitona (25 un)", "extra": 29.75 },
        { "label": "Tartelette de Presunto (25 un)", "extra": 29.75 },
        { "label": "Barquete com Salpicão (25 un)", "extra": 44.75 },
        { "label": "Barquete com Presunto (25 un)", "extra": 42.25 },
        { "label": "Barquete com Queijo (25 un)", "extra": 42.25 },
        { "label": "Barquete com Frango (25 un)", "extra": 42.25 },
        { "label": "Chipa (500 gramas)", "extra": 44.95 },
        { "label": "Pão de Queijo (500 gramas)", "extra": 43.45 }
      ], 
      "type": "multiple"
    }
  },

  {
    "id": 26,
    "category": "Salgados",
    "name": "Mini Sanduíches",
    "description": "Para comprar um cento (100 un), basta selecionar o mesmo sabor 4 vezes.",
    "image": "/static/images/MiniSanduiches.jpg",
    "base_price": 0.00,
    "bestseller": False,
    "options": {
      "sabores": [
        { "label": "Frango (25 un)", "extra": 39.75 },
        { "label": "Presunto (25 un)", "extra": 39.75 },
        { "label": "Atum (25 un)", "extra": 42.25 },
        { "label": "Peito de peru (25 un)", "extra": 42.25 },
        { "label": "Quatro queijos (25 un)", "extra": 42.25 }
      ], 
      "type": "multiple"
    }
  },

  {
    "id": 27,
    "category": "Salgados",
    "name": "Mini Pizza Pré-Assada",
    "description": "Para comprar um cento (100 un), basta selecionar o mesmo sabor 4 vezes. Produto pré assado.",
    "image": "/static/images/MiniPizza.jpg",
    "base_price": 0.00,
    "bestseller": False,
    "options": {
      "sabores": [
        { "label": "Muçarela com Azeitona (25 un)", "extra": 32.25 },
        { "label": "Frango (25 un)", "extra": 32.25 },
        { "label": "Muçarela (25 un)", "extra": 32.25 },
        { "label": "Presunto (25 un)", "extra": 32.25 }
      ], 
      "type": "multiple"
    }
  },

  {
    "id": 28,
    "category": "Salgados",
    "name": "Pão de Queijo",
    "image": "/static/images/PaoQueijo.jpg",
    "base_price": 0.00,
    "bestseller": True,
    "options": {
      "sabores": [
        { "label": "0.5 kg", "extra": 43.45 },
        { "label": "1.0 kg", "extra": 86.90 },
        { "label": "1.5 kg", "extra": 130.35 },
        { "label": "2.0 kg", "extra": 173.80 }
      ], 
      "type": "single"
    }
  },

  {
    "id": 29,
    "category": "Salgados",
    "name": "Chipa",
    "image": "/static/images/Chipa.jpg",
    "base_price": 0.00,
    "bestseller": False,
    "options": {
      "sabores": [
        { "label": "0.5 kg", "extra": 44.95 },
        { "label": "1.0 kg", "extra": 89.90 },
        { "label": "1.5 kg", "extra": 134.85 },
        { "label": "2.0 kg", "extra": 179.80 }
      ], 
      "type": "single"
    }
  },

  {
    "id": 30,
    "category": "Bebidas",
    "name": "Coca-cola (2 Litros)",
    "image": "/static/images/CocaCola.jpg",
    "base_price": 14.90,
    "bestseller": True
  },

  {
    "id": 31,
    "category": "Bebidas",
    "name": "Coca-cola Zero (2 Litros)",
    "image": "/static/images/CocaZero.jpg",
    "base_price": 14.90,
    "bestseller": True
  },

  {
    "id": 32,
    "category": "Bebidas",
    "name": "Fanta Laranja (2 Litros)",
    "image": "/static/images/FantaLaranja.jpg",
    "base_price": 14.90,
    "bestseller": False
  },

  {
    "id": 33,
    "category": "Bebidas",
    "name": "Sprite (2 Litros)",
    "image": "/static/images/Sprite.jpg",
    "base_price": 14.90,
    "bestseller": False
  },

  {
    "id": 34,
    "category": "Bebidas",
    "name": "Guaraná Antárctica (2 Litros)",
    "image": "/static/images/Guarana.jpg",
    "base_price": 14.90,
    "bestseller": True
  },

  {
    "id": 35,
    "category": "Bebidas",
    "name": "Guaraná Antárctica Zero (2 Litros)",
    "image": "/static/images/GuaranaZero.jpg",
    "base_price": 14.90,
    "bestseller": False
  },

  {
    "id": 36,
    "category": "Bebidas",
    "name": "Suco Del Valle de Abacaxi (1 Litro)",
    "image": "/static/images/SucoAbacaxi.jpg",
    "base_price": 10.90,
    "bestseller": False
  },

  {
    "id": 37,
    "category": "Bebidas",
    "name": "Suco Del Valle de Manga (1 Litro)",
    "image": "/static/images/SucoManga.jpg",
    "base_price": 10.90,
    "bestseller": False
  },

  {
    "id": 38,
    "category": "Bebidas",
    "name": "Suco Del Valle de Caju (1 Litro)",
    "image": "/static/images/SucoCaju.jpg",
    "base_price": 10.90,
    "bestseller": False
  },

  {
    "id": 39,
    "category": "Bebidas",
    "name": "Suco Del Valle de Pêssego (1 litro)",
    "image": "/static/images/SucoPessego.jpg",
    "base_price": 10.90,
    "bestseller": False
  }
]

    for it in provided:
        cur.execute('INSERT INTO menu_items (id, category, name, base_price, description, picture_url, bestseller) VALUES (?,?,?,?,?,?,?)',
                    (it.get('id'), it.get('category'), it.get('name'), it.get('base_price') or 0.0, it.get('description'), it.get('image'), 1 if it.get('bestseller') else 0))
        menu_id = cur.lastrowid if cur.lastrowid else it.get('id')
        # Insert options groups
        opts = it.get('options') or {}
        group_type = opts.get('type') if isinstance(opts, dict) else None
        for k, v in (opts.items() if isinstance(opts, dict) else []):
            if k == 'type':
                continue
            # create option group
            cur.execute('INSERT INTO option_groups (menu_item_id, `key`, type) VALUES (?,?,?)', (menu_id, k, group_type or 'single'))
            og_id = cur.lastrowid
            # insert options
            for choice in v:
                label = choice.get('label')
                extra = choice.get('extra', 0.0)
                cur.execute('INSERT INTO options (menu_item_id, option_group_id, name, price_modifier) VALUES (?,?,?,?)', (menu_id, og_id, label, extra))
        # mark best seller initial count
        if it.get('bestseller'):
            cur.execute('INSERT OR REPLACE INTO best_sellers (menu_item_id, count) VALUES (?,?)', (menu_id, 10))
    conn.commit()

def row_to_dict(row):
    return {k: row[k] for k in row.keys()}

@app.route('/')
def index():
    return render_template('index.html', company_website=COMPANY_WEBSITE)

@app.route('/api/menu')
def api_menu():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT * FROM menu_items')
    items = [row_to_dict(r) for r in cur.fetchall()]

    for it in items:
        cur.execute('SELECT id, `key`, type FROM option_groups WHERE menu_item_id = ?', (it['id'],))
        groups = [row_to_dict(g) for g in cur.fetchall()]
        opts_struct = {}
        for g in groups:
            cur.execute('SELECT id, name, price_modifier FROM options WHERE option_group_id = ?', (g['id'],))
            choices = []
            for o in cur.fetchall():
                oo = dict(o)
                choices.append({'id': oo['id'], 'label': oo['name'], 'extra': oo['price_modifier']})
            opts_struct[g['key']] = {'type': g['type'], 'choices': choices}
        it['options'] = opts_struct

        it['bestseller'] = bool(it.get('bestseller'))
    conn.close()
    return jsonify({'menu': items})

@app.route('/api/categories')
def api_categories():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT DISTINCT category FROM menu_items WHERE category IS NOT NULL ORDER BY category')
    categories = [row[0] for row in cur.fetchall()]
    conn.close()
    return jsonify({'categories': categories})

@app.route('/api/category/<category_name>')
def api_category(category_name):
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT * FROM menu_items WHERE category = ?', (category_name,))
    items = [row_to_dict(r) for r in cur.fetchall()]
    
    for it in items:
        cur.execute('SELECT id, `key`, type FROM option_groups WHERE menu_item_id = ?', (it['id'],))
        groups = [row_to_dict(g) for g in cur.fetchall()]
        opts_struct = {}
        for g in groups:
            cur.execute('SELECT id, name, price_modifier FROM options WHERE option_group_id = ?', (g['id'],))
            choices = []
            for o in cur.fetchall():
                oo = dict(o)
                choices.append({'id': oo['id'], 'label': oo['name'], 'extra': oo['price_modifier']})
            opts_struct[g['key']] = {'type': g['type'], 'choices': choices}
        it['options'] = opts_struct
        it['bestseller'] = bool(it.get('bestseller'))
    
    conn.close()
    return jsonify({'items': items, 'category': category_name})

@app.route('/api/best_sellers')
def api_best_sellers():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('''SELECT m.*, b.count FROM best_sellers b JOIN menu_items m ON b.menu_item_id = m.id ORDER BY b.count DESC LIMIT 10''')
    items = []
    for r in cur.fetchall():
        row = row_to_dict(r)
        items.append(row)
    conn.close()
    return jsonify({'best_sellers': items})

@app.route('/api/best_sellers_categories')
def api_best_sellers_categories():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('''SELECT DISTINCT m.category FROM best_sellers b 
                   JOIN menu_items m ON b.menu_item_id = m.id 
                   WHERE m.category IS NOT NULL ORDER BY m.category''')
    categories = [row[0] for row in cur.fetchall()]
    conn.close()
    return jsonify({'categories': categories})

@app.route('/api/best_sellers_category/<category_name>')
def api_best_sellers_category(category_name):
    conn = get_db()
    cur = conn.cursor()
    cur.execute('''SELECT m.*, b.count FROM best_sellers b 
                   JOIN menu_items m ON b.menu_item_id = m.id 
                   WHERE m.category = ? 
                   ORDER BY b.count DESC''', (category_name,))
    items = []
    for r in cur.fetchall():
        row = row_to_dict(r)
        items.append(row)
    conn.close()
    return jsonify({'items': items, 'category': category_name})

@app.route('/api/create_cart', methods=['POST'])
def api_create_cart():
    data = request.get_json() or {}
    cart_id = data.get('cart_id')
    if not cart_id:
        cart_id = os.urandom(16).hex()
    conn = get_db()
    cur = conn.cursor()
    cur.execute('INSERT OR IGNORE INTO carts (id, created_at) VALUES (?,?)', (cart_id, datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()
    return jsonify({'cart_id': cart_id})

@app.route('/api/add_to_cart', methods=['POST'])
def api_add_to_cart():
    data = request.get_json() or {}
    cart_id = data.get('cart_id')
    menu_item_id = data.get('menu_item_id')
    selected_options = data.get('selected_options', [])
    quantity = int(data.get('quantity', 1))
    if not cart_id or not menu_item_id:
        return jsonify({'error':'cart_id and menu_item_id required'}), 400
    conn = get_db()
    cur = conn.cursor()
    
    cur.execute('SELECT base_price FROM menu_items WHERE id = ?', (menu_item_id,))
    row = cur.fetchone()
    if not row:
        return jsonify({'error':'menu item not found'}), 404
    base_price = row['base_price']
    unit_price = base_price
    
    if selected_options:
        
        placeholders = ','.join('?' for _ in selected_options)
        cur.execute(f'SELECT SUM(price_modifier) as total_modifier FROM options WHERE id IN ({placeholders})', selected_options)
        res = cur.fetchone()
        modifier = res['total_modifier'] or 0.0
        unit_price += modifier
    
    cur.execute('INSERT INTO cart_items (cart_id, menu_item_id, selected_options, quantity, unit_price) VALUES (?,?,?,?,?)',
                (cart_id, menu_item_id, json.dumps(selected_options), quantity, unit_price))
    
    cur.execute('INSERT INTO best_sellers (menu_item_id, count) VALUES (?,?) ON CONFLICT(menu_item_id) DO UPDATE SET count = count + ?', (menu_item_id, quantity, quantity))
    conn.commit()
    conn.close()
    return jsonify({'status':'ok'})

@app.route('/api/cart/<cart_id>')
def api_cart(cart_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT * FROM cart_items WHERE cart_id = ?', (cart_id,))
    items = []
    for r in cur.fetchall():
        row = row_to_dict(r)
        
        cur.execute('SELECT name, description FROM menu_items WHERE id = ?', (row['menu_item_id'],))
        m = cur.fetchone()
        if m:
            row['menu_item_name'] = m['name']
        row['selected_options'] = json.loads(row['selected_options']) if row['selected_options'] else []
        items.append(row)
    conn.close()
    total = sum(i['unit_price'] * i['quantity'] for i in items)
    return jsonify({'items': items, 'total': total})

@app.route('/api/remove_item', methods=['POST'])
def api_remove_item():
    data = request.get_json() or {}
    item_id = data.get('cart_item_id')
    if not item_id:
        return jsonify({'error':'cart_item_id required'}), 400
    conn = get_db()
    cur = conn.cursor()
    cur.execute('DELETE FROM cart_items WHERE id = ?', (item_id,))
    conn.commit()
    conn.close()
    return jsonify({'status':'ok'})

@app.route('/api/suggestions', methods=['POST'])
def api_suggestions():
    data = request.get_json() or {}
    qty = int(data.get('quantidade_de_pessoas', 1))
    party_type = (data.get('tipo_de_festa') or '').lower()
    location = data.get('localização') or ''

    conn = get_db()
    cur = conn.cursor()
    suggestions = []

    mapping = {
        'casamento': ['Tortas Especialidades', 'Tortas', 'Doces', 'Bolos', 'Bebidas'],
        'aniversário': ['Tortas Especialidades', 'Tortas', 'Bolos', 'Doces'],
        'formal': ['Tortas Especialidades', 'Salgados', 'Bebidas'],
        'reunião': ['Salgados', 'Bebidas', 'Bolos'],
    }
    
    categories = mapping.get(party_type, mapping['aniversário'])

    discount = 0.0
    if qty > 50:
        discount = 0.10

    placeholders = ','.join('?' * len(categories))
    query = f'SELECT id, name, base_price, description, category FROM menu_items WHERE category IN ({placeholders}) ORDER BY bestseller DESC, name ASC'
    cur.execute(query, categories)
    items = [row_to_dict(r) for r in cur.fetchall()]

    for item in items:
        base_price = item['base_price']
        est_total = 0.0

        if base_price == 0.0:
            
            if 'Sanduíches' in item['name'] or 'Salgados' in item['category']:
                est_total = (qty / 25) * 40.0  
            elif 'Bombons' in item['name'] or 'Doces' in item['category']:
                est_total = (qty / 50) * 67.0  
            elif 'Bolo' in item['name']:
                est_total = (qty / 10) * 45.0  
            else:
                est_total = qty * 2.0 
        else:
            
            if 'Bebidas' in item['category']:
                est_total = (qty / 5) * base_price  
            else:
                est_total = base_price * max(1, qty // 10)  

        est_discounted = est_total * (1 - discount)
        suggestions.append({
            'id': item['id'],
            'name': item['name'],
            'category': item['category'],
            'estimate': round(est_discounted, 2),
            'discount_applied': discount > 0.0
        })

    conn.close()
    return jsonify({'sugestões': suggestions, 'desconto': discount, 'quantidade_de_pessoas': qty})

@app.route('/api/checkout', methods=['POST'])
def api_checkout():
    data = request.get_json() or {}
    cart_id = data.get('cart_id')
    if not cart_id:
        return jsonify({'error':'cart_id required'}), 400
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT * FROM cart_items WHERE cart_id = ?', (cart_id,))
    items = [row_to_dict(r) for r in cur.fetchall()]
    if not items:
        return jsonify({'erro':'carrinho vazio'}), 400

    lines = []
    total = 0.0
    for i in items:
        cur.execute('SELECT name FROM menu_items WHERE id = ?', (i['menu_item_id'],))
        m = cur.fetchone()
        name = m['name'] if m else ('item-'+str(i['menu_item_id']))
        opts = json.loads(i['selected_options']) if i['selected_options'] else []
        item_subtotal = i['unit_price'] * i['quantity']

        # Formatação do item
        item_line = f"{i['quantity']} x {name:<30} R$ {item_subtotal:>7.2f}"
        lines.append(item_line)
        
        # Opções do item
        if opts:
            placeholders = ','.join('?' for _ in opts)
            cur.execute(f'SELECT name FROM options WHERE id IN ({placeholders})', opts)
            opt_names = [r['name'] for r in cur.fetchall()]
            options_str = ", ".join(opt_names)
            lines.append(f"     └─ {options_str}")
        
        total += item_subtotal
    
    # Formata o resumo como um recibo bonito
    separator = "=" * 55
    summary = f"\n{separator}\n"
    summary += "       PEDIDO - MORADA MINEIRA\n"
    summary += f"{separator}\n\n"
    summary += "Qtd | Produto                    | Valor\n"
    summary += "-" * 55 + "\n"
    summary += "\n".join(lines) + "\n\n"
    summary += "-" * 55 + "\n"
    summary += f"TOTAL{' ' * (55 - 18 - len(f'R$ {total:>7.2f}'))}R$ {total:>7.2f}\n"
    summary += f"{separator}\n"
    summary += "Obrigado pela sua compra!\n"
    summary += f"{separator}"
    conn.close()

    text = f"Novo pedido:\n{summary}"
    wa_msg = quote_plus(text)
    wa_link = f"https://api.whatsapp.com/send?phone={COMPANY_WHATSAPP_NUMBER}&text={wa_msg}"
    return jsonify({'whatsapp_link': wa_link, 'resumo': summary})

@app.route('/support')
def support():
    return redirect(COMPANY_WEBSITE)

@app.route('/api/message', methods=['POST'])
def api_message():
    """Simple rule-based chatbot handling key intents: menu, carrinho, add, remover, sugestões, mais vendidos, suporte, finalizar."""
    data = request.get_json() or {}
    text = (data.get('message') or '').lower()
    cart_id = data.get('cart_id')
    # Detect intents by keywords
    if any(k in text for k in ['menu', 'mostrar menu', 'ver menu', 'show menu']):
        return jsonify({'type':'menu', 'text':'Aqui está o nosso menu.', 'action':'open_menu'})
    if any(k in text for k in ['mais vendidos', 'favoritos', 'recomendados', 'popular', 'best sellers']):
        return jsonify({'type':'mais_vendidos', 'text':'Esses são os nossos favoritos.', 'action':'open_best_sellers'})
    if any(k in text for k in ['carrinho', 'mostrar carrinho', 'ver carrinho', 'cart', 'show cart']):
        return jsonify({'type':'carrinho', 'text':'Abrindo o seu carrinho.', 'action':'open_cart'})
    if any(k in text for k in ['add', 'eu quero', 'comprar', 'pedir']):
        return jsonify({'type':'add', 'text':'Qual item você gostaria de adicionar?'})
    if any(k in text for k in ['sugestão', 'sugestões', 'não sei']):
        return jsonify({'type':'sugestões', 'text':'Me diga a quantidade de pessoas, tipo de festa e localização.'})
    if any(k in text for k in ['finalizar','parar de comprar','parar','acabei','só isso', 'sair']):
        return jsonify({'type':'finalizar', 'text':'Pronto para finalizar. Seu pedido será mandado para o WhatsApp.'})
    if any(k in text for k in ['suporte','ajuda','website', 'support']):
        return jsonify({'type':'suporte', 'text':'Abrindo o site', 'action':'open_support'})
    # default
    return jsonify({'type':'não sei', 'text':"Desculpa, eu não entendi. Você pode me pedir para mostrar o menu, carrinho, sugestões ou a finalização da sua compra."})

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
