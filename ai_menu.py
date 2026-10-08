import json
import random

with open("menu.json", "r", encoding="utf-8") as file:
    menu = json.load(file)

products = menu["products"]

keywords = {
    "курица": ["курица", "куриный", "куриное", "цыпленок", "цыплёнок"],
    "мясо": [
        "мясо",
        "говядина",
        "говядиной",
        "говяжий",
        "баранина",
        "бараний",
        "свинина",
        "свиной",
    ],
    "рыба": [
        "рыба",
        "рыбный",
        "рыбное",
        "сибас",
        "лосось",
        "форель",
        "тунец",
        "сёмга",
        "семга",
    ],
    "морепродукты": [
        "морепродукты",
        "креветки",
        "креветка",
        "мидии",
        "мидия",
        "кальмар",
        "кальмары",
    ],
}


def find_products(search, max_price, spicy=False, exclude_ids=None):
    result = []

    if exclude_ids is None:
        exclude_ids = set()
    else:
        exclude_ids = set(exclude_ids)

    if isinstance(search, str):
        search = [search]

    search_words = []

    for search_item in search:
        search_item = search_item.lower()

        words = keywords.get(search_item, [search_item])

        search_words.extend(words)

    for product in products:

        if not product["available"]:
            continue

        # Не показываем уже показанные блюда
        if product["id"] in exclude_ids:
            continue

        tags = [tag.lower() for tag in product["tags"]]

        # Не показываем острые блюда,
        # если клиент не хочет острое
        if spicy is False and "острая" in tags:
            continue

        found = False

        for word in search_words:
            if word in tags:
                found = True
                break

        if found and product["price"] <= max_price:
            result.append(product)

    return result


def get_main_dishes_count(people):
    return people


def is_main_dish(product):
    main_categories = ["cat-main-dishes", "cat-burgers", "cat-pasta", "cat-pizza"]

    return product["category"] in main_categories


def is_extra_dish(product):
    extra_categories = ["cat-salads", "cat-appetizers"]

    return product["category"] in extra_categories


def make_recommendation(search, people, budget, spicy=False, exclude_ids=None):
    # Уже показанные блюда
    if exclude_ids is None:
        exclude_ids = set()
    else:
        exclude_ids = set(exclude_ids)

    if budget == 0:
        budget = 100000

    if isinstance(search, str):
        search = [search]

    target_budget = budget - 500

    if target_budget < 0:
        target_budget = budget

    result = []
    total = 0

    main_count = get_main_dishes_count(people)

    # Ищем блюда отдельно для каждой категории
    for search_item in search:

        found_products = find_products([search_item], target_budget, spicy, exclude_ids)

        main_dishes = []

        for product in found_products:
            if is_main_dish(product):
                main_dishes.append(product)

        random.shuffle(main_dishes)

        for product in main_dishes:

            if total + product["price"] <= target_budget:
                result.append(product)
                total += product["price"]
                break

    # Если категорий меньше, чем нужно блюд
    if len(result) < main_count:

        found_products = find_products(search, target_budget, spicy, exclude_ids)

        main_dishes = []

        for product in found_products:
            if is_main_dish(product):
                main_dishes.append(product)

        random.shuffle(main_dishes)

        for product in main_dishes:

            if product in result:
                continue

            if len(result) >= main_count:
                break

            if total + product["price"] <= target_budget:
                result.append(product)
                total += product["price"]

    # Дополнительные блюда
    extra_dishes = []

    for product in products:

        if not product["available"]:
            continue

        # Не показываем уже показанные блюда
        if product["id"] in exclude_ids:
            continue

        if not is_extra_dish(product):
            continue

        tags = [tag.lower() for tag in product["tags"]]

        if spicy is False and "острая" in tags:
            continue

        extra_dishes.append(product)

    random.shuffle(extra_dishes)

    for product in extra_dishes:

        if total + product["price"] <= target_budget:
            result.append(product)
            total += product["price"]
            break

    return result, total
