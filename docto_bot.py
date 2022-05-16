import requests
import datetime
import smtplib, ssl

def read_centers(centers_file):
    print('Reading centers list ...')
    with open(centers_file, 'r') as filin:
        centers = [line[:-1] for line in filin]
    return centers

def get_info(centers, header):   
    print('Getting centers info ...') 
    infos = [requests.get(url=f'https://www.doctolib.fr/booking/{center}.json', 
                         headers=header).json()['data'] for center in centers]
    return infos

def extract_param(infos):
    agendas_id = [info['agendas'][0]['id'] for info in infos]
    visit_motive_ids = [info['visit_motives'][0]['id'] for info in infos]
    practise_id = [info['places'][0]['id'].split('-')[1] for info in infos]
    
    return agendas_id, visit_motive_ids, practise_id

def send_email(credential_file, receiver, center):
    port = 465
    context = ssl.create_default_context()
    with open(credential_file, 'r') as filin:
        login = filin.readline().split(':')[1][:-1]
        password = filin.readline().split(':')[1][:-1]
    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login(login, password)
        server.sendmail(login, receiver, f'I have found a free slot for the center {center} !')

def check_slot(params, centers, header, span):
        i = 0
        print('Checking slot ...')
        for aid, vid, pid in zip(params[0], params[1], params[2]):
            meta = {"start_date": datetime.datetime.today().date().isoformat(),
                    "visit_motive_ids": vid,
                    "agenda_ids": aid,
                    "insurance_sector": "public",
                    "practice_ids" : pid,
                    "limit": str(span)}
            
            get = requests.get(url='https://www.doctolib.fr/availabilities.json', 
                   params=meta,
                   headers=header).json()
            if get['total'] > 0:
                send_email(credential_file='credentials.txt', 
                           receiver='atheos119@gmail.com',
                           center=centers[i])
            i += 1

header = {'User-Agent': 'xxx'}
centers = read_centers('centers.txt')

infos = get_info(centers, header)
params = extract_param(infos)
check_slot(params, centers, header, 15)
print('Done !')
