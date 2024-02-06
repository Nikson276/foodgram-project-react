import json


def handle():
    with open('testdb.json', 'rb') as f:
        data = json.load(f)
        print(data)

        for item in data:
            print(f'НОВАЯ СТРОКА: {item}')
            for key in item:
                print(f'KEY - {key}, VALUE - {item.get(key)}')
                
                # for j in data.get(i):
                #     print(f'ЗНАЧЕНИЕ: {j}')
                #     # s = SubGenre()
                #     # s.name = j
                #     # s.save()
                #     # s.genres.add(g)
    print('finished')


handle()
