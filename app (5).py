from io import BytesIO

import numpy as np
import requests
import streamlit as st
from PIL import Image

from ai_functions import generate_image, apply_filter

st.title("AI Creative Studio")
st.write("Опиши, яке зображення хочеш отримати")

prompt = st.text_area("Ваш промпт:", placeholder="Наприклад: кіт-астронавт на Місяці")

STYLES = {
    "Без стилю": "",
    "Реалістичний": "high detail, photorealistic, natural lighting",
    "Акварель": "watercolor painting style, soft edges, pastel colors",
    "Мультяшний": "3D animated movie style, vibrant colors, friendly look",
    "Піксель-Арт": "pixel art style, 16-bit retro game aesthetic"
}

FILTERS = [
    "Без фільтра", "Чорно-біле", "Розмиття", "Контури", "Сепія",
    "Віддзеркалення", "Налаштування яскравості", "Налаштування контрасту",
    "Колірний сплеск"
]

styles_choice = st.selectbox("Стилі:", list(STYLES.keys()))

if st.button("Згенерувати зображення"):
    if prompt.strip() == "":
        st.warning("Ти ще нічого не написав. Опиши, що намалювати, і спробуй ще раз")
    else:
        final_prompt = prompt.strip()
        if STYLES[styles_choice] != "":
            final_prompt = final_prompt + ", " + STYLES[styles_choice]

        try:
            with st.spinner("AI малює твоє зображення, це може зайняти до хвилини"):
                image_bytes, error = generate_image(final_prompt)

            if error:
                st.error(f"Не вдалося згенерувати зображення: {error}")
            else:
                st.session_state["image"] = image_bytes
                st.session_state["style"] = styles_choice
                st.success("Готово! Тепер можеш обрати фільтр або одразу завантажити картинку")

        except requests.exceptions.Timeout:
            st.error("Сервіс довго не відповідає. Зачекай хвилинку і натисни кнопку ще раз")
        except Exception:
            st.error("Щось пішло не так. Перевір інтернет і спробуй ще раз або зміни опис")

if "image" in st.session_state:
    img_array = np.array(Image.open(BytesIO(st.session_state["image"])).convert("RGB"))

    filter_option = st.selectbox("Фільтр:", FILTERS)
    value = None
    color = "Червоний"

    if filter_option == "Налаштування яскравості":
        value = st.slider("Рівень яскравості", -100, 100, 0)
    elif filter_option == "Налаштування контрасту":
        value = st.slider("Рівень контрасту", 0.5, 3.0, 1.0, step=0.1)
    elif filter_option == "Колірний сплеск":
        color = st.selectbox("Колір, який залишити", ["Червоний", "Зелений", "Синій"])

    result = apply_filter(img_array, filter_option, value, color)
    st.image(result, caption=f"Стиль: {st.session_state['style']}, фільтр: {filter_option}", use_container_width=True)

    buf = BytesIO()
    Image.fromarray(result).save(buf, format="PNG")

    st.download_button(
        label="Завантажити",
        data=buf.getvalue(),
        file_name="ai_result.png",
        mime="image/png"
    )
