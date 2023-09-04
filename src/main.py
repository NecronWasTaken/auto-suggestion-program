import sqlite3
from thefuzz import fuzz
from thefuzz import process
from PIL import Image, ImageDraw, ImageFont
import cv2
import numpy as np
from scipy.spatial.distance import euclidean
from skimage.feature import hog
from skimage import exposure

cities_codes = ["АР", "БН", "БӨ", "БР", "БУ", "ГА",
                "ГС", "ДА", "ДГ", "ДО", "ДУ", "ЗА",
                "НА", "ОР", "ӨВ", "ӨМ", "СБ", "СҮ",
                "СЭ", "ТӨ", "УА", "УБ", "УН", "УЕ", "УВ",
                "ХО", "ХӨ", "ХЦ", "ХЭ", "ЦА", "ЧО", "ЭТ"]

set_of_cities_codes = set(cities_codes)

cc1 = {'А': 0, 'Б': 1, 'Г': 3, 'Д': 4, 'З': 8, 'Н': 14, 'О': 15,
       'Ө': 16, 'С': 19, 'Т': 20, 'У': 21, 'Х': 24, 'Ц': 25, 'Ч': 26, 'Э': 32}
cc2 = {'А': 0, 'Б': 1, 'В': 2, 'Г': 3, 'Е': 5, 'М': 13, 'Н': 14, 'О': 15,
       'Ө': 16, 'Р': 18, 'С': 19, 'Т': 20, 'У': 21, 'Ү': 22, 'Ц': 25, 'Э': 32}

alphabet = ["А", "Б", "В", "Г", "Д", "Е",
            "Ё", "Ж", "З", "И", "Й", "К",
            "Л", "М", "Н", "О", "Ө", "П",
            "Р", "С", "Т", "У", "Ү", "Ф",
            "Х", "Ц", "Ч", "Ш", "Щ", "Ъ",
            "Ы", "Ь", "Э", "Ю", "Я"]

numbers = ["0", "1", "2", "3", "4",
           "5", "6", "7", "8", "9"]

set_of_alphabet = set(alphabet)


def generate_combinations(cur: sqlite3.Cursor) -> list[str]:
    ans = []
    id = 0
    for i in range(0, 10000):
        for code in cities_codes:
            for letter in alphabet:
                ans.append(f'{i:04d}' + code + letter)
    return ans


def get_plate_numbers_from_DB() -> list:
    con = sqlite3.connect("data.db")
    cur = con.cursor()
    # cur.execute("CREATE TABLE plateNumbers(id, plate_number)")
    # ans = generate_combinations(cur)
    # for i in range(len(ans)):
    #     cur.execute("""
    #                     INSERT INTO plateNumbers VALUES (?,?)
    #                 """, (i,ans[i]))
    # con.commit()
    res = cur.execute("SELECT * FROM plateNumbers")
    return res.fetchall()


def text_to_image(text: str, font_size=40, image_size=(50, 50)):
    font = ImageFont.truetype("fonts/Roboto-Regular.ttf", font_size)
    image = Image.new("L", image_size, 255)
    draw = ImageDraw.Draw(image)
    draw.text((10, 0), text, font=font, fill=0)
    return image


def compute_hog(image) -> np.ndarray:
    fd = hog(image, orientations=8, pixels_per_cell=(
        5, 5), cells_per_block=(1, 1), visualize=True)[0]
    return fd


def calculate_distance(feature1: np.ndarray, feature2: np.ndarray):
    return np.linalg.norm(feature1 - feature2)


def plate_number_validation(plate: str) -> list[bool] | None:
    mask = [True] * 7

    if (len(plate) != 7):
        print('Incorrect length of Plate Number')
        return None

    for i in range(4):
        try:
            int(plate[i])
        except:
            mask[i] = False

    if (not plate[4:6] in set_of_cities_codes):
        mask[4], mask[5] = False, False

    if (not plate[6] in set_of_alphabet):
        mask[6] = False

    return mask


def get_array_of_features(chars: list) -> list[np.ndarray]:
    ans = []
    for char in chars:
        image = text_to_image(char)
        ans.append(compute_hog(image))

    return ans


def create_dump_of_distances() -> None:
    chars = numbers + alphabet
    features = get_array_of_features(chars)

    arr = np.zeros((len(chars), len(chars)))

    for i in range(len(chars)):
        for j in range(i + 1, len(chars)):
            arr[i][j] = calculate_distance(features[i], features[j])
            arr[j][i] = arr[i][j]
    np.savetxt('dump_of_distances.txt', arr)
    return


def get_closest_chars_and_distances(char: str, target_chars: list[str], count: int, target_chars_distances: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    idx = np.argpartition(target_chars_distances, count)
    chars = np.array(target_chars)[idx[:count]]
    distances = target_chars_distances[idx[:count]]

    return (np.delete(chars, np.where(chars == char)), np.delete(distances, np.where(distances == 0)))


def create_dump_of_closest_chars_and_distances(dump_of_distances: np.ndarray, target_chars: list[str], count: tuple[int, int], target_range: tuple[int, int], type_name: str) -> None:
    chars = []
    distances = []
    for i in range(10):
        closest = get_closest_chars_and_distances(
            numbers[i], target_chars, count[0], dump_of_distances[i][target_range[0]:target_range[1]])
        chars.append(closest[0])
        distances.append(closest[1])
    for i in range(len(alphabet)):
        closest = get_closest_chars_and_distances(
            alphabet[i], target_chars, count[1], dump_of_distances[i+10][target_range[0]:target_range[1]])
        chars.append(closest[0])
        distances.append(closest[1])
    print(chars)
    np.savetxt('dump_of_closest_chars_'+type_name+'.txt',
               np.array(chars), delimiter=" ", fmt="%s", encoding='utf-8')
    np.savetxt('dump_of_closest_distances_' +
               type_name+'.txt', np.array(distances))
    return


def main() -> None:
    # plate_numbers = get_plate_numbers_from_DB()

    # print(len(plate_numbers))
    # print(plate_numbers[:10])

    # print("Fuzz ration: ", fuzz.ratio("0000АРА", "0000АРА"))

    # create_dump_of_distances()
    dump_of_distances = np.loadtxt('dump_of_distances.txt')
    # print(dump_of_distances)
    create_dump_of_closest_chars_and_distances(
        dump_of_distances, numbers, (4, 3), (0, 10), '1-4')

    create_dump_of_closest_chars_and_distances(
        dump_of_distances, alphabet, (3, 4), (10, len(numbers+alphabet)), '7')
    dump_of_closest_chars = np.loadtxt(
        'dump_of_closest_chars_1-4.txt', dtype=str, encoding='utf-8')
    dump_of_closest_distances = np.loadtxt('dump_of_closest_distances_1-4.txt')
    # print(dump_of_closest_chars)
    # print(dump_of_closest_distances)

    print('...')


if __name__ == '__main__':
    main()
