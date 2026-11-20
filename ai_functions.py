import urllib.parse
import requests
import cv2
import numpy as np

def generate_image(prompt):
    encoded_prompt = urllib.parse.quote(prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&nologo=true&seed=42"

    response = requests.get(url, timeout=45)

    if response.status_code == 200:
        return response.content, None
    else:
        return None, f"Сервіс тимчасово недоступний: ({response.status_code})"


def apply_filter(img_array, filter_name, value=None, color="Червоний"):
    if filter_name == "Чорно-біле":
        return cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)

    if filter_name == "Розмиття":
        return cv2.GaussianBlur(img_array, (15, 15), 0)

    if filter_name == "Контури":
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        return cv2.Canny(gray, 100, 200)

    if filter_name == "Сепія":
        kernel = np.array([[0.393, 0.769, 0.189],
                           [0.349, 0.686, 0.168],
                           [0.272, 0.534, 0.131]])
        result = cv2.transform(img_array, kernel)
        return np.clip(result, 0, 255).astype(np.uint8)

    if filter_name == "Віддзеркалення":
        return cv2.flip(img_array, 1)

    if filter_name == "Налаштування яскравості":
        return cv2.convertScaleAbs(img_array, alpha=1.0, beta=value)

    if filter_name == "Налаштування контрасту":
        return cv2.convertScaleAbs(img_array, alpha=value, beta=0)

    if filter_name == "Колірний сплеск":
        hsv = cv2.cvtColor(img_array, cv2.COLOR_RGB2HSV)

        if color == "Червоний":
            mask1 = cv2.inRange(hsv, np.array([0, 50, 50]), np.array([10, 255, 255]))
            mask2 = cv2.inRange(hsv, np.array([170, 50, 50]), np.array([180, 255, 255]))
            mask = mask1 + mask2
        elif color == "Зелений":
            mask = cv2.inRange(hsv, np.array([35, 50, 50]), np.array([85, 255, 255]))
        else:
            mask = cv2.inRange(hsv, np.array([100, 50, 50]), np.array([130, 255, 255]))

        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        gray = cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)
        mask = np.stack([mask, mask, mask], axis=2)
        return np.where(mask > 0, img_array, gray)

    return img_array


if __name__ == "__main__":
    print("Перевірка generate_image")
    image_bytes, error = generate_image("a red cat, simple drawing")

    if error:
        print("Помилка:", error)
    else:
        print("Зображення отримано, розмір:", len(image_bytes), "байт")
