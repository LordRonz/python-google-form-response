#!/usr/bin/env python3

import sys

def main():
    import re, requests, multiprocessing, random
    url = input('Target url: ')
    url = sys.argv[1] if len(sys.argv) > 1 else url
    if not url.startswith('https://') and not url.startswith('http://'):
        url = 'https://' + url

    ua = ''
    try:
        with open('user-agents.txt', 'rb') as f:
            line = next(f)
            rr = random.randrange
            for num, f in enumerate(f, 2):
                if rr(num):
                    continue
                line = f
            ua = line.strip()
    except FileNotFoundError:
        pass

    ua = ua if ua else b'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0'

    header = {'Referer': url, 'User-Agent': ua}
    http = requests.get(url)
    url = http.url
    submit_url = url.replace('viewform', 'formResponse')
    if not http.ok:
        print(f'Error {http.status_code}')
        return

    is_number = lambda x: x.strip().isdigit()
    pattern = r'\[\d*,"[ -~]*",[\w\s]*,[\w\d\s]*,\[\[\d*'
    result = re.findall(pattern, http.text)

    entries = [f"entry.{a.split(',')[-1][2:]}" for a in result]
    questions = [a.split(',')[1][1:-1] for a in result]
    answers = []

    for q in questions:
        n = input(f'number of answers for question "{q}" : ')
        while not is_number(n) or int(n) < 1:
            print('Invalid input !')
            n = input(f'number of answers for question "{q}" : ')
        n = int(n)
        answers.append([input(f'Answer #{i + 1}: ') for i in range(n)])
    chances = []
    for q, a in zip(questions, answers):
        tmp = []
        for ans in a:
            n = input(f'Chances of getting "{ans}" for question "{q}" (percentage): ')
            while not is_number(n):
                print('Invalid input !')
                n = input(f'Chances of getting "{ans}" for question "{q}" (percentage): ')
            tmp.append(int(n))
        chances.append(tmp)

    n_of_response = input(f'How many responses? ')
    while not is_number(n_of_response):
        print('Invalid input !')
        n_of_response = input(f'How many responses? ')
    n_of_response = int(n_of_response)
    
    sent_response = 0

    print("Please Wait...")

    def form():
        form_data = {}
        for entry, answer, chance in zip(entries, answers, chances):
            form_data[entry] = random.choices(answer, weights=chance, k=1)[0]

        r = requests.post(submit_url, data=form_data, headers=header)
        if r.ok:
            return_queue.put(1)
        else:
            return_queue.put(0)

    processes = []
    return_queue = multiprocessing.Queue()

    for _ in range(n_of_response):
        p = multiprocessing.Process(target=form)
        p.start();
        processes.append(p)

    for process in processes:
        process.join()
        sent_response += return_queue.get()
    
    print(f'Done !\nSent response : {sent_response}')

if __name__ == "__main__":
    main()
