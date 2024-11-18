import  requests

def getChallan(vehNum):
  try:
    response = requests.get(

    f'https://www.carinfo.app/_next/data/hm-m2SjgXpXP-9U8s1GuM/challan-details/{vehNum}.json'
    )
    data  = response.json()
    header_element = data['pageProps']['challanDetailsResponse']['data']['headerElement']
    challans =  data['pageProps']['challanDetailsResponse']['data']['challans']
    return header_element, challans
  except requests.exceptions.RequestException as e:
    print("Error making the request:", e)
  except ValueError as e:
    print("Error parsing JSON response:", e)


def get_ekey(vehnum):

  headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:132.0) Gecko/20100101 Firefox/132.0',
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.5',
    # 'Accept-Encoding': 'gzip, deflate, br, zstd',
    'Referer': 'https://www.acko.com/gi/car-journey/car-number?cardType=car-number',
    'content-type': 'application/json',
    'newrelic': 'eyJ2IjpbMCwxXSwiZCI6eyJ0eSI6IkJyb3dzZXIiLCJhYyI6IjIxMDAwOTgiLCJhcCI6IjExMzQyOTcxMzMiLCJpZCI6ImRlMDc5ZWJjYmQ4ZTkyNDgiLCJ0ciI6IjY1ZDBiMGJmNzRkYWFiNWMwYjlhMWU5ZjVhOGIwNzIwIiwidGkiOjE3MzE4ODI5ODY3MzV9fQ==',
    'traceparent': '00-65d0b0bf74daab5c0b9a1e9f5a8b0720-de079ebcbd8e9248-01',
    'tracestate': '2100098@nr=0-1-2100098-1134297133-de079ebcbd8e9248----1731882986735',
    'x-app-name': 'falcon',
    'x-landing-path': '/lp/new-comprehensive',
    'x-landing-url': 'https://www.acko.com/gi/car-journey/car-number?cardType=car-number',
    'Origin': 'https://www.acko.com',
    'Connection': 'keep-alive',
    'Cookie': '__cf_bm=u5oi_AOJ5nMIv6jPmr0Bet8PKT2wNpxQ7bIq4cIiXRA-1731882924-1.0.1.1-NMmXph5AHkbCOY_Ytc.0hq6xxcLj274uvK7QSWiE3KbR7_mtuyQWJgyyA4GjnbUec.IxY.URAw821Z6K5NHeMg; trackerid=050c1ff8-71f3-40a0-901a-00524811f1e5; acko_visit=85G3jYYh0IsIbAnRJaBnYQ; _gcl_au=1.1.1831566983.1731882927; _ga_W47KBK64MF=GS1.1.1731882926.1.1.1731882950.36.0.0; _ga=GA1.2.1133921548.1731882927; _gid=GA1.2.291998332.1731882928; _fbp=fb.1.1731882928044.270232626128050648; _hjSessionUser_3252132=eyJpZCI6IjE5YTY0NzEzLWY5MmQtNTBkMy04YzcyLTI3ZTM4MzM1NDE1ZiIsImNyZWF0ZWQiOjE3MzE4ODI5MjgxNDAsImV4aXN0aW5nIjp0cnVlfQ==; _hjSession_3252132=eyJpZCI6ImZlOWIwNWI1LTlkNTctNDk3NS1hZTZlLTRlMTMzZmY3ZWVjMiIsImMiOjE3MzE4ODI5MjgxNDAsInMiOjAsInIiOjAsInNiIjowLCJzciI6MCwic2UiOjAsImZzIjoxLCJzcCI6MH0=; _gat_gtag_UA_92272448_1=1; _gat_UA-92272448-1=1; wisepops_visits=%5B%222024-11-17T22%3A35%3A26.561Z%22%5D; we_aid=1c75d1d171684f009dea064cc6aea02fa0314fe1; wisepops=%7B%22popups%22%3A%7B%7D%2C%22sub%22%3A0%2C%22ucrn%22%3A59%2C%22cid%22%3A%2267186%22%2C%22v%22%3A5%2C%22bandit%22%3A%7B%22recos%22%3A%7B%7D%7D%7D; _uetsid=3ebd7cd0a53411efaf65e3a75491ff82; _uetvid=3ebd8ce0a53411efa40a070b17602a39; wisepops_visitor=%7B%22AgGNMkk7M8%22%3A%22ad8f37b4-24a1-440f-a21d-4eab95511a86%22%7D; wisepops_session=%7B%22arrivalOnSite%22%3A%222024-11-17T22%3A35%3A26.561Z%22%2C%22mtime%22%3A1731882950859%2C%22pageviews%22%3A3%2C%22popups%22%3A%7B%7D%2C%22bars%22%3A%7B%7D%2C%22sticky%22%3A%7B%7D%2C%22countdowns%22%3A%7B%7D%2C%22src%22%3Anull%2C%22utm%22%3A%7B%7D%2C%22testIp%22%3Anull%7D',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'Priority': 'u=0',
    # Requests doesn't support trailers
    # 'TE': 'trailers',
  }

  json_data = {
    'registration_number': vehnum,
    'phone': '',
    'origin': 'acko',
    'product': 'car',
    'is_new': False,
  }

  response = requests.post(
    'https://www.acko.com/motororchestrator/api/v2/proposals',
    headers=headers,
    json=json_data,
  )
  return response.json()['ekey']


def get_vehicle_details(vehnum):
  try:
      response = requests.get(
        f'https://www.acko.com/motororchestrator/api/v2/proposals/{get_ekey(vehnum)}',
      )
      return response.json()
  except:
    return "no"


