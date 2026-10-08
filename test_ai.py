import json

from ai_service import analyze_request
from ai_menu import make_recommendation

message = "Нас 3 человека, бюджет 3000 сом. Хотим что-нибудь мясное."

ai_result = analyze_request(message)
print("AI RESULT:", ai_result)

print("ОТВЕТ AI:")
print(ai_result)


data = json.loads(ai_result)
from ai_menu import find_products

found = find_products(data["search"], data["budget"], data["spicy"])

print("НАЙДЕНО БЛЮД:", len(found))

for product in found:
    print(product["name"], "-", product["price"], product["category"])


recommendations, total = make_recommendation(
    data["search"], data["people"], data["budget"], data["spicy"]
)


print()
print("РЕКОМЕНДАЦИЯ MON AMI:")
print()

for product in recommendations:
    print(product["name"], "-", product["price"], "сом")

print()
print("ИТОГО:", total, "сом")
