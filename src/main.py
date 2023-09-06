from itertools import permutations
from re import T
import sqlite3
from thefuzz import fuzz
from thefuzz import process
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from skimage.feature import hog
from modules.auto_suggestion import *


def generate_combinations(cur: sqlite3.Cursor) -> list[str]:
    ans = []
    id = 0
    for i in range(0, 10000):
        for code in cities_codes:
            for letter in alphabet:
                ans.append(f'{i:04d}' + code + letter)
    return ans


def save_generated_plate_numbers_to_DB() -> None:
    con = sqlite3.connect("data.db")
    cur = con.cursor()
    cur.execute("CREATE TABLE plateNumbers(id, plate_number)")
    ans = generate_combinations(cur)
    for i in range(len(ans)):
        cur.execute("""
                        INSERT INTO plateNumbers VALUES (?,?)
                    """, (i, ans[i]))
    con.commit()
    return


def get_plate_numbers_from_DB() -> list[tuple[int, str]]:
    con = sqlite3.connect("data.db")
    cur = con.cursor()
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
    np.savetxt('dumps/dump_of_distances.txt', arr)
    return


def get_closest_chars_and_distances(char: str, target_chars: list[str], target_chars_distances: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    idx = np.argpartition([target_chars_distances[i] + 20 if char == target_chars[i]
                          else target_chars_distances[i] for i in range(len(target_chars_distances))], 3)
    chars = np.array(target_chars)[idx[:3]]
    distances = target_chars_distances[idx[:3]]

    return (np.delete(chars, np.where(chars == char)), np.delete(distances, np.where(distances == 0)))


def create_dump_of_closest_chars_and_distances(dump_of_distances: np.ndarray, target_is_numbers: bool, target_list: list[str], type_name: str) -> None:
    if target_is_numbers:
        target_chars = numbers
        range1, range2 = 0, 10
    else:
        target_chars = alphabet
        range1, range2 = 10, len(dump_of_distances[0])
    chars = []
    distances = []
    set_of_target_list = set(target_list)

    for i in range(10):
        closest = get_closest_chars_and_distances(
            numbers[i], target_chars, dump_of_distances[i][range1:range2])
        chars.append(closest[0])
        distances.append(closest[1])
    for i in range(len(alphabet)):
        arr = dump_of_distances[i+10][range1:range2]
        closest = get_closest_chars_and_distances(
            alphabet[i], target_chars, np.array([arr[j] if alphabet[j] in set_of_target_list else arr[j]+10 for j in range(len(arr))]))
        chars.append(closest[0])
        distances.append(closest[1])

    np.savetxt('dumps/dump_of_closest_chars_' + type_name + '.txt',
               np.array(chars), delimiter=" ", fmt="%s", encoding='utf-8')
    np.savetxt('dumps/dump_of_closest_distances_' +
               type_name+'.txt', np.array(distances))
    return


def calculate_distance_between_pairs(dump_of_distances: np.ndarray, s1: str, s2: str) -> float:
    distance = 0.0
    for i in range(2):
        if s1[i] != s2[i]:
            distance += dump_of_distances[dict_of_chars[s1[i]]][dict_of_chars[s2[i]]]
    return distance

def create_dump_of_closest_cc(dump_of_distances: np.ndarray) -> None:
    this_chars = []
    distances = []
    pairs = list(map( ''.join ,permutations(chars, 2))) + [chars[i] + chars[i] for i in range(len(chars))]
    print(len(pairs))
    for pair in pairs:
        arr = []
        for cc in cities_codes:
            arr.append(calculate_distance_between_pairs(dump_of_distances, pair, cc))
        closest = np.argpartition(arr, 4)[:3]

        temp1 = [cities_codes[close] for close in closest]
        temp2 = [arr[close] for close in closest]

        this_chars.append(np.delete(temp1, np.where(temp1 == pair)))
        distances.append(np.delete(temp2, np.where(temp2 == 0)))

    np.savetxt('dumps/dump_of_closest_chars_pairs.txt',
               np.array(pairs), delimiter=" ", fmt="%s", encoding='utf-8')
    np.savetxt('dumps/dump_of_closest_chars_cc.txt',
               np.array(this_chars), delimiter=" ", fmt="%s", encoding='utf-8')
    np.savetxt('dumps/dump_of_closest_distances_cc.txt', np.array(distances))
    return

def main() -> None:
    # create_dump_of_distances()
    dump_of_distances: np.ndarray = np.loadtxt(
        'dumps/dump_of_distances.txt', dtype="float") 
    # print(dump_of_distances)

    # create_dump_of_closest_chars_and_distances(
    #     dump_of_distances, True, alphabet ,'1-4')
    # create_dump_of_closest_chars_and_distances(
    #     dump_of_distances, False, cc1,'5')
    # create_dump_of_closest_chars_and_distances(
    #     dump_of_distances, False, cc2,'6')
    # create_dump_of_closest_chars_and_distances(
    #     dump_of_distances, False, alphabet,'7')
    # create_dump_of_closest_cc(dump_of_distances)

    number = 'ПОРС110'
    inc = plate_number_validation(number)

    if inc is not None:
        print(find_closest_numbers(number, inc))
    print('...')

if __name__ == '__main__':
    main()
