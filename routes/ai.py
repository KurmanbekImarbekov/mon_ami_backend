from fastapi import APIRouter, HTTPException
import json

from schemas.ai import AIRequest
from ai_service import analyze_request
from ai_menu import make_recommendation

router = APIRouter()


@router.post("/ai/recommend")
def ai_recommend(request: AIRequest):

    try:
        # 1. AI понимает запрос клиента
        ai_result = analyze_request(request.message)

        # 2. Превращаем JSON AI в Python-словарь
        data = json.loads(ai_result)

        # 3. Получаем уже показанные блюда
        exclude_ids = request.exclude_ids

        # 4. Ищем реальные блюда в menu.json
        recommendations, total = make_recommendation(
            data["search"], data["people"], data["budget"], data["spicy"], exclude_ids
        )

        # 5. Отправляем результат обратно
        return {"request": data, "recommendations": recommendations, "total": total}

    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))
