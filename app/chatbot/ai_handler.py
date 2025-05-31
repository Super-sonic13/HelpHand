import os
import google.generativeai as genai
import re

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")

def get_gemini_response(message):
    try:
        prompt = (
            message.strip() +
            "\n\nВідповідай лише у чистому Markdown. Не використовуй подвійні чи одинарні зірочки для виділення тексту, якщо це не markdown-форматування (жирний, курсив, списки). Не додавай зайвих зірочок у тексті. Нові абзаци — через подвійний ентер. Не пиши жодних зірочок у тексті, якщо це не частина списку або markdown-форматування."
        )
        response = model.generate_content(prompt)
        text = response.text if hasattr(response, 'text') else str(response)
        # Пост-обробка: видалити зайві зірочки, якщо вони не є markdown
        # Видалити зірочки, які не є частиною markdown (наприклад, **text** або *text*)
        # Залишаємо тільки ті, що оточують слова (markdown), інші видаляємо
        text = re.sub(r'(?<!\*)\*{1,2}(?![\w\s])', '', text)  # зірочки не біля слова
        text = re.sub(r'(?<![\w\s])\*{1,2}(?!\*)', '', text)  # зірочки не біля слова
        # Додатково: замінити \n на подвійний ентер для markdown
        text = text.replace('\n', '\n\n')
        return text
    except Exception as e:
        print(f"[Gemini ERROR]: {e}")
        return "Сталася помилка при обробці вашого запиту."