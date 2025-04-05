#!/usr/bin/env python3
"""
JSON QA Agent
------------
An agent that loads JSON data and answers questions based on that data.
"""

import json
import re
import sys

class JsonQAAgent:
    def __init__(self, json_file_path):
        """Initialize the agent with a JSON data file."""
        self.json_file_path = json_file_path
        self.data = self.load_json_data()
        
        # Define question patterns and their corresponding handler functions
        self.question_handlers = [
            # Product related questions
            {
                "patterns": [
                    r"(.*)(価格|料金|値段|いくら)(.*)(ノートパソコン|パソコン|ラップトップ)(.*)",
                    r"(.*)(ノートパソコン|パソコン|ラップトップ)(.*)(価格|料金|値段|いくら)(.*)",
                    r"(.*)(laptop|notebook)(.*)(price|cost)(.*)",
                    r"(.*)(price|cost)(.*)(laptop|notebook)(.*)"
                ],
                "handler": self.get_product_price,
                "product_name": "ノートパソコン"
            },
            {
                "patterns": [
                    r"(.*)(価格|料金|値段|いくら)(.*)(スマートフォン|スマホ|携帯)(.*)",
                    r"(.*)(スマートフォン|スマホ|携帯)(.*)(価格|料金|値段|いくら)(.*)",
                    r"(.*)(smartphone|phone)(.*)(price|cost)(.*)",
                    r"(.*)(price|cost)(.*)(smartphone|phone)(.*)"
                ],
                "handler": self.get_product_price,
                "product_name": "スマートフォン"
            },
            {
                "patterns": [
                    r"(.*)(価格|料金|値段|いくら)(.*)(ヘッドフォン|ヘッドホン)(.*)",
                    r"(.*)(ヘッドフォン|ヘッドホン)(.*)(価格|料金|値段|いくら)(.*)",
                    r"(.*)(headphone)(.*)(price|cost)(.*)",
                    r"(.*)(price|cost)(.*)(headphone)(.*)"
                ],
                "handler": self.get_product_price,
                "product_name": "ワイヤレスヘッドフォン"
            },
            {
                "patterns": [
                    r"(.*)(スペック|仕様|性能)(.*)(ノートパソコン|パソコン|ラップトップ)(.*)",
                    r"(.*)(ノートパソコン|パソコン|ラップトップ)(.*)(スペック|仕様|性能)(.*)",
                    r"(.*)(laptop|notebook)(.*)(spec|specification)(.*)",
                    r"(.*)(spec|specification)(.*)(laptop|notebook)(.*)"
                ],
                "handler": self.get_product_specs,
                "product_name": "ノートパソコン"
            },
            {
                "patterns": [
                    r"(.*)(スペック|仕様|性能)(.*)(スマートフォン|スマホ|携帯)(.*)",
                    r"(.*)(スマートフォン|スマホ|携帯)(.*)(スペック|仕様|性能)(.*)",
                    r"(.*)(smartphone|phone)(.*)(spec|specification)(.*)",
                    r"(.*)(spec|specification)(.*)(smartphone|phone)(.*)"
                ],
                "handler": self.get_product_specs,
                "product_name": "スマートフォン"
            },
            {
                "patterns": [
                    r"(.*)(在庫|ストック|入荷)(.*)(ノートパソコン|パソコン|ラップトップ)(.*)",
                    r"(.*)(ノートパソコン|パソコン|ラップトップ)(.*)(在庫|ストック|入荷)(.*)",
                    r"(.*)(laptop|notebook)(.*)(stock|available)(.*)",
                    r"(.*)(stock|available)(.*)(laptop|notebook)(.*)"
                ],
                "handler": self.get_product_availability,
                "product_name": "ノートパソコン"
            },
            {
                "patterns": [
                    r"(.*)(在庫|ストック|入荷)(.*)(スマートフォン|スマホ|携帯)(.*)",
                    r"(.*)(スマートフォン|スマホ|携帯)(.*)(在庫|ストック|入荷)(.*)",
                    r"(.*)(smartphone|phone)(.*)(stock|available)(.*)",
                    r"(.*)(stock|available)(.*)(smartphone|phone)(.*)"
                ],
                "handler": self.get_product_availability,
                "product_name": "スマートフォン"
            },
            {
                "patterns": [
                    r"(.*)(在庫|ストック|入荷)(.*)(ヘッドフォン|ヘッドホン)(.*)",
                    r"(.*)(ヘッドフォン|ヘッドホン)(.*)(在庫|ストック|入荷)(.*)",
                    r"(.*)(headphone)(.*)(stock|available)(.*)",
                    r"(.*)(stock|available)(.*)(headphone)(.*)"
                ],
                "handler": self.get_product_availability,
                "product_name": "ワイヤレスヘッドフォン"
            },
            # FAQ related questions
            {
                "patterns": [
                    r"(.*)(返品|返金|キャンセル)(.*)",
                    r"(.*)(return|refund|cancel)(.*)"
                ],
                "handler": self.get_faq_answer,
                "keyword": "返品"
            },
            {
                "patterns": [
                    r"(.*)(配送|発送|届く|到着)(.*)(時間|日数|かかる)(.*)",
                    r"(.*)(shipping|delivery)(.*)(time|long)(.*)"
                ],
                "handler": self.get_faq_answer,
                "keyword": "配送"
            },
            {
                "patterns": [
                    r"(.*)(国際|海外)(.*)(配送|発送)(.*)",
                    r"(.*)(international|overseas)(.*)(shipping|delivery)(.*)"
                ],
                "handler": self.get_faq_answer,
                "keyword": "国際配送"
            },
            # Company related questions
            {
                "patterns": [
                    r"(.*)(会社|企業)(.*)(名前|名称)(.*)",
                    r"(.*)(company)(.*)(name)(.*)"
                ],
                "handler": self.get_company_name
            },
            {
                "patterns": [
                    r"(.*)(会社|企業)(.*)(場所|所在地|住所|どこ)(.*)",
                    r"(.*)(company)(.*)(location|address|where)(.*)"
                ],
                "handler": self.get_company_locations
            },
            {
                "patterns": [
                    r"(.*)(連絡|問い合わせ|コンタクト)(.*)(方法|手段|どうやって)(.*)",
                    r"(.*)(contact|reach)(.*)(how|information)(.*)"
                ],
                "handler": self.get_company_contact
            },
            # General product questions
            {
                "patterns": [
                    r"(.*)(商品|製品)(.*)(一覧|リスト|何|教えて)(.*)",
                    r"(.*)(products|items)(.*)(list|available|what)(.*)"
                ],
                "handler": self.list_products
            }
        ]
    
    def load_json_data(self):
        """Load and parse the JSON data file."""
        try:
            with open(self.json_file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"JSONファイルの読み込み中にエラーが発生しました: {e}")
            sys.exit(1)
    
    def find_product_by_name(self, product_name):
        """Find a product in the data by its name."""
        for product in self.data.get("products", []):
            if product_name in product.get("name", ""):
                return product
        return None
    
    def get_product_price(self, question, product_name):
        """Get the price of a specific product."""
        product = self.find_product_by_name(product_name)
        if product and "price" in product:
            return f"{product['name']}の価格は{product['price']:,}円です。"
        return f"申し訳ありませんが、{product_name}の価格情報が見つかりませんでした。"
    
    def get_product_specs(self, question, product_name):
        """Get the specifications of a specific product."""
        product = self.find_product_by_name(product_name)
        if product and "specs" in product:
            specs = product["specs"]
            specs_text = ", ".join([f"{k}: {v}" for k, v in specs.items()])
            return f"{product['name']}のスペックは以下の通りです：\n{specs_text}"
        return f"申し訳ありませんが、{product_name}のスペック情報が見つかりませんでした。"
    
    def get_product_availability(self, question, product_name):
        """Check if a specific product is in stock."""
        product = self.find_product_by_name(product_name)
        if product and "inStock" in product:
            if product["inStock"]:
                return f"{product['name']}は現在在庫があります。"
            else:
                return f"申し訳ありませんが、{product['name']}は現在在庫切れです。"
        return f"申し訳ありませんが、{product_name}の在庫情報が見つかりませんでした。"
    
    def get_faq_answer(self, question, keyword):
        """Find an FAQ answer based on a keyword."""
        for faq in self.data.get("faq", []):
            if keyword in faq.get("question", ""):
                return faq.get("answer", "情報が見つかりませんでした。")
        return "申し訳ありませんが、その質問に対する回答が見つかりませんでした。"
    
    def get_company_name(self, question):
        """Get the company name."""
        company = self.data.get("company", {})
        if "name" in company:
            return f"会社名は{company['name']}です。"
        return "申し訳ありませんが、会社名の情報が見つかりませんでした。"
    
    def get_company_locations(self, question):
        """Get the company locations."""
        company = self.data.get("company", {})
        if "locations" in company:
            locations = ", ".join(company["locations"])
            return f"会社の所在地は{locations}です。"
        return "申し訳ありませんが、会社の所在地情報が見つかりませんでした。"
    
    def get_company_contact(self, question):
        """Get the company contact information."""
        company = self.data.get("company", {})
        contact_info = company.get("contactInfo", {})
        if contact_info:
            email = contact_info.get("email", "不明")
            phone = contact_info.get("phone", "不明")
            address = contact_info.get("address", "不明")
            return f"連絡先情報：\nメール: {email}\n電話: {phone}\n住所: {address}"
        return "申し訳ありませんが、連絡先情報が見つかりませんでした。"
    
    def list_products(self, question):
        """List all available products."""
        products = self.data.get("products", [])
        if products:
            product_list = "\n".join([f"- {p['name']}: {p['price']:,}円" for p in products])
            return f"取り扱い商品一覧：\n{product_list}"
        return "申し訳ありませんが、商品情報が見つかりませんでした。"
    
    def process_question(self, question):
        """Process a user question and return an answer."""
        # Check each question handler pattern
        for handler_info in self.question_handlers:
            for pattern in handler_info["patterns"]:
                if re.search(pattern, question, re.IGNORECASE):
                    # Call the appropriate handler function
                    if "product_name" in handler_info:
                        return handler_info["handler"](question, handler_info["product_name"])
                    elif "keyword" in handler_info:
                        return handler_info["handler"](question, handler_info["keyword"])
                    else:
                        return handler_info["handler"](question)
        
        # If no patterns match, return a default response
        return "申し訳ありませんが、その質問に答えることができません。別の質問を試してみてください。"
    
    def run(self):
        """Run the agent in an interactive loop."""
        print("JSON QA エージェントが起動しました。'exit'と入力すると終了します。")
        print("JSONデータに基づいて質問に答えます。例：「ノートパソコンの価格はいくらですか？」")
        
        while True:
            user_input = input("\nあなた: ")
            
            if user_input.lower() == "exit":
                print("エージェントを終了します。")
                break
            
            response = self.process_question(user_input)
            print(f"エージェント: {response}")


if __name__ == "__main__":
    # Check if a JSON file path is provided as a command-line argument
    if len(sys.argv) > 1:
        json_file_path = sys.argv[1]
    else:
        json_file_path = "knowledge_base.json"  # Default JSON file
    
    # Create and run the agent
    agent = JsonQAAgent(json_file_path)
    agent.run()
