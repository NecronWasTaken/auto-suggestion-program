import numpy as np

cities_codes = ["АР", "БН", "БӨ", "БР", "БУ", "ГА",
                "ГС", "ДА", "ДГ", "ДО", "ДУ", "ЗА",
                "НА", "ОР", "ӨВ", "ӨМ", "СБ", "СҮ",
                "СЭ", "ТӨ", "УА", "УБ", "УН", "УЕ", "УВ",
                "ХО", "ХӨ", "ХЦ", "ХЭ", "ЦА", "ЧО", "ЭТ"]

set_of_cities_codes = set(cities_codes)

cc1 = ['У', 'Г', 'Н', 'Ц', 'С', 'Ч', 'З',
       'Э', 'Д', 'О', 'Т', 'Х', 'А', 'Ө', 'Б']
cc2 = ['А', 'С', 'У', 'Э', 'Н', 'В', 'Ө', 'О',
       'Г', 'Б', 'Р', 'М', 'Ц', 'Т', 'Е', 'Ү']

alphabet = ["А", "Б", "В", "Г", "Д", "Е",
            "Ё", "Ж", "З", "И", "Й", "К",
            "Л", "М", "Н", "О", "Ө", "П",
            "Р", "С", "Т", "У", "Ү", "Ф",
            "Х", "Ц", "Ч", "Ш", "Щ", "Ъ",
            "Ы", "Ь", "Э", "Ю", "Я"]

numbers = ["0", "1", "2", "3", "4",
           "5", "6", "7", "8", "9"]

chars = numbers + alphabet

dict_of_chars = {'0': 0, '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, 'А': 10, 'Б': 11, 'В': 12, 'Г': 13, 'Д': 14, 'Е': 15, 'Ё': 16, 'Ж': 17, 'З': 18, 'И': 19, 'Й': 20, 'К': 21,
                 'Л': 22, 'М': 23, 'Н': 24, 'О': 25, 'Ө': 26, 'П': 27, 'Р': 28, 'С': 29, 'Т': 30, 'У': 31, 'Ү': 32, 'Ф': 33, 'Х': 34, 'Ц': 35, 'Ч': 36, 'Ш': 37, 'Щ': 38, 'Ъ': 39, 'Ы': 40, 'Ь': 41, 'Э': 42, 'Ю': 43, 'Я': 44}

set_of_alphabet = set(alphabet)
set_of_numbers = set(numbers)

dump_of_closest_chars_1 = np.loadtxt(
    'dumps/dump_of_closest_chars_1-4.txt', dtype=str, encoding='utf-8')
dump_of_closest_distances_1 = np.loadtxt(
    'dumps/dump_of_closest_distances_1-4.txt')

dump_of_closest_chars_4 = np.loadtxt(
    'dumps/dump_of_closest_chars_5.txt', dtype=str, encoding='utf-8')
dump_of_closest_distances_4 = np.loadtxt('dumps/dump_of_closest_distances_5.txt')

dump_of_closest_chars_5 = np.loadtxt(
    'dumps/dump_of_closest_chars_6.txt', dtype=str, encoding='utf-8')
dump_of_closest_distances_5 = np.loadtxt('dumps/dump_of_closest_distances_6.txt')

dump_of_closest_chars_6 = np.loadtxt(
    'dumps/dump_of_closest_chars_7.txt', dtype=str, encoding='utf-8')
dump_of_closest_distances_6 = np.loadtxt('dumps/dump_of_closest_distances_7.txt')

dump_of_closest_chars_cc = np.loadtxt(
    'dumps/dump_of_closest_chars_cc.txt', dtype=str, encoding='utf-8')
dump_of_closest_distances_cc = np.loadtxt('dumps/dump_of_closest_distances_cc.txt')
dump_of_closest_chars_pairs = np.loadtxt(
    'dumps/dump_of_closest_chars_pairs.txt', dtype=str, encoding='utf-8')

def partial_permutations(elements, length) -> list[list[int]]:
    if length == 0:
        return [[]]
    else:
        partials = []
        for element in elements:
            sub_partials = partial_permutations(elements, length - 1)
            for sub_partial in sub_partials:
                partials.append([element] + sub_partial)
        return partials


def plate_number_validation(plate: str) -> list[int] | None:
    incorrect = []

    if (len(plate) != 7):
        print('Incorrect length of Plate Number')
        return None

    for i in range(7):
        if plate[i] not in set_of_numbers and plate[i] not in set_of_alphabet:
            incorrect.append(i+1)

    if len(incorrect) > 0:
        print('Incorrect symbols at: ')
        print(incorrect)
        return None

    for i in range(4):
        try:
            int(plate[i])
        except:
            incorrect.append(i)

    if (not plate[4:6] in set_of_cities_codes):
        incorrect += [4, 5]

    if (not plate[6] in set_of_alphabet):
        incorrect.append(6)

    return incorrect


def find_closest_numbers(number: str, inc: list[int]) -> str:
    chars = numbers + alphabet
    print("Find closest numbers to:", number)

    if len(inc) == 0:
        mins = []
        chars = []
        for i in range(4):
            index = np.argmin(dump_of_closest_distances_1[int(number[i])])
            chars.append(dump_of_closest_chars_1[int(number[i])][index])
            mins.append(dump_of_closest_distances_1[int(number[i])][index])

        index = np.argmin(
            dump_of_closest_distances_4[dict_of_chars[number[4]]])
        chars.append(dump_of_closest_chars_4[dict_of_chars[number[4]]][index])
        mins.append(
            dump_of_closest_distances_4[dict_of_chars[number[4]]][index])

        index = np.argmin(
            dump_of_closest_distances_5[dict_of_chars[number[5]]])
        chars.append(dump_of_closest_chars_5[dict_of_chars[number[5]]][index])
        mins.append(
            dump_of_closest_distances_5[dict_of_chars[number[5]]][index])

        index = np.argmin(
            dump_of_closest_distances_6[dict_of_chars[number[6]]])
        chars.append(dump_of_closest_chars_6[dict_of_chars[number[6]]][index])
        mins.append(
            dump_of_closest_distances_6[dict_of_chars[number[6]]][index])

        closest = np.argpartition(mins, 3)

        l = []
        for i in range(3):
            new_num = number[:closest[i]] + \
                chars[closest[i]] + number[closest[i]+1:7]
            l.append(new_num)

        return ",".join(l)

    partial_perms = partial_permutations([0, 1, 2], len(inc))

    l = []
    s = set()
    for perm in partial_perms:
        new_num = ''
        distance = 0.0
        k = 0
        for i in range(4):
            if i in inc:
                new_num += dump_of_closest_chars_1[dict_of_chars[number[i]]][perm[k]]
                distance += dump_of_closest_distances_1[dict_of_chars[number[i]]][perm[k]]
                k += 1
            else:
                new_num += number[i]
        if 4 in inc:
            cc = dump_of_closest_chars_4[dict_of_chars[number[4]]][perm[k]] + dump_of_closest_chars_5[dict_of_chars[number[5]]][perm[k+1]]
            index = np.where(dump_of_closest_chars_pairs==cc)[0][0]
            new_num += dump_of_closest_chars_cc[index][perm[k]]
            distance += dump_of_closest_distances_cc[index][perm[k]]
            k += 2
        else:
            new_num += number[4] + number[5]
        if 6 in inc:
            index6 = dict_of_chars[number[6]]
            new_num += dump_of_closest_chars_6[index6][perm[k]]
            distance += dump_of_closest_distances_6[index6][perm[k]]
            k += 1
        else:
            new_num += number[6]
        if new_num not in s:
            s.add(new_num)
            l.append((new_num, distance))

    return ','.join([a[0] for a in sorted(l, key=lambda a: a[1])[:3]])
