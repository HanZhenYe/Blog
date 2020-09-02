

data = [
    {
        'name': '第一章',
        'id': 12,
        'er': [
            {
                'name': '1.1 需求',
                'id': 13,
                'xi': True,
                'san': [
                    {
                        'name': '1.1.1 分析',
                        'id': 4,
                    }
                ]
            },
            {
                'name': '1.2 分析',
                'id': 5,
                'xi': False
            }
        ]
    }
]

for da in data:
    print(da['name'])
    for d in da['er']:
        print(' '*4, d['name'])
        if d['xi']:
            for n in d['san']:
                print(' '*8, n['name'])
