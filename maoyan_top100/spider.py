import json
import os
import re
import time
from multiprocessing import Lock, Pool, Process, RLock

import requests
import user_agent
from requests.exceptions import RequestException

filename = 'result.txt'
file_path = os.path.join(os.getcwd(), filename)


headers = {'user-agent': user_agent.generate_user_agent()}


def get_one_page(url):
    try:
        resp = requests.get(url, headers=headers)
        if resp.status_code == 200:
            print("Download-Success {}".format(url))
            return resp.text
        return None
    except RequestException:
        print("Download-Failed {}".format(url))
        return None


def parse_one_page(html):
    pattern = re.compile('<dd>.*?board-index.*?>(\d+)</i>.*?' +
                         'data-src="(.*?)".*?' +
                         'name">.*?>(.*?)</a>.*?' +
                         'star">(.*?)</p>.*?' +
                         'releasetime">(.*?)</p>.*?' +
                         'score">.*?integer">(.*?)</i>.*?fraction">(.*?)</i>.*?</dd>', re.S
                         )
    items = re.findall(pattern, html)
    for i in items:
        yield {
            'index': i[0],
            'image': i[1],
            'title': i[2],
            'actor': i[3].strip()[3:],
            'time': i[4].strip()[5:],
            'score': i[5]+i[6]
        }


def write_to_file(data):
    with open(file_path, 'a', encoding='utf-8') as f:
        for i in data:
            f.write(json.dumps(i, ensure_ascii=False) + '\n')


def main(offset):
    url = 'http://maoyan.com/board/4?offset={}'.format(offset)
    html = get_one_page(url)
    data = [i for i in parse_one_page(html)]
    return data


if __name__ == '__main__':
    start = time.time()
    if os.path.exists(file_path):
        os.remove(file_path)
    pool = Pool()
    for i in range(10):
        pool.apply_async(main, args=(i*10,), callback=write_to_file)
    pool.close()
    pool.join()
    print("Cost: {} S".format(time.time() - start))
