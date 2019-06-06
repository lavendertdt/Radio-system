import requests
import json

ADDRESS = 'http://localhost:8765'

requests.post(ADDRESS + '/ratios/100',
              json={
                  'alias': 'Radio100',
                  'allowed_locations': ['CPH-1', 'CPH-2']
              })

requests.post(ADDRESS + '/ratios/101',
              json={
                  'alias': 'Radio101',
                  'allowed_locations': ['CPH-1', 'CPH-2', 'CPH-3']
              })

requests.post(ADDRESS + '/ratios/100/location', json={'location': 'CPH-1'})
requests.post(ADDRESS + '/ratios/101/location', json={'location': 'CPH-3'})
requests.post(ADDRESS + '/ratios/100/location', json={'location': 'CPH-3'})
requests.get(ADDRESS + '/ratios/101/location')
requests.get(ADDRESS + '/ratios/100/location')

requests.post(ADDRESS + '/ratios/102',
              json={
                  'alias': 'Radio102',
                  'allowed_locations': ['CPH-1', 'CPH-2', 'CPH-3']
              })

response = requests.get(ADDRESS + '/ratios/102/location')

try:
    print('json', response.json())
except json.decoder.JSONDecodeError:
    print('text', response.text)
