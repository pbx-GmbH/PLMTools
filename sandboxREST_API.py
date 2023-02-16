import requests


url = "https://live.upchain.net"

# response = requests.get('https://live.upchain.net/api/auth/v1/companies')
# print(response)

access_token_body = {
    "grant_type": "password",
    "username": "dominik.radler@pbx.at",
    "password": "A1.Js3DeRS",
    "client_id": "Georg_Pongratz_API",
    "client_secret": "sabDotYAxRZCZtxcRv5Pdi3uJynJjAbl"
}

resp = requests.post("https://live-sso.upchain.net/auth/realms/upchain/protocol/openid-connect/token", data=access_token_body)
#
access_token = resp.json()['access_token']
# access_token = 'eyJhbGciOiJSUzI1NiIsInR5cCEIgOiAiSldUIiwia2lkIiA6ICJlRGhQc3MwQVZwOFZEb0taVFVPQnJHYXo5V01EUExqdVVtRTNuOUZ1VG1jIn0.eyJleHAiOjE2NzExNDU0NDksImlhdCI6MTY3MTExNjY0OSwianRpIjoiNzYwNjA5Y2MtNWRlMy00MTcwLWIxM2EtZWRiZTNhOTBlYTA2IiwiaXNzIjoiaHR0cHM6Ly9saXZlLXNzby51cGNoYWluLm5ldC9hdXRoL3JlYWxtcy91cGNoYWluIiwic3ViIjoiOTE0NjUxN2MtYWFjYi00YjIzLWE3YTQtYThjODU5YzU4ZDRkIiwidHlwIjoiQmVhcmVyIiwiYXpwIjoiR2VvcmdfUG9uZ3JhdHpfQVBJIiwic2Vzc2lvbl9zdGF0ZSI6ImQ0MDVkMmFjLTg2MTUtNGQ1MC04MjA4LTNmZmQ1MTlhOTVjMCIsImFjciI6IjEiLCJhbGxvd2VkLW9yaWdpbnMiOlsiaHR0cHM6Ly9saXZlLnVwY2hhaW4ubmV0Il0sInNjb3BlIjoicHJvZmlsZSBlbWFpbCB3cml0ZSByZWFkIiwic2lkIjoiZDQwNWQyYWMtODYxNS00ZDUwLTgyMDgtM2ZmZDUxOWE5NWMwIiwiY29tcGFueUlkcyI6WzQ5NV0sImVtYWlsX3ZlcmlmaWVkIjp0cnVlLCJhdXRvZGVza191c2VyX2lkIjoiUjVRSllTNUxRTFJRS0c2SiIsIm5hbWUiOiJEb21pbmlrIFJhZGxlciIsInByZWZlcnJlZF91c2VybmFtZSI6ImRvbWluaWsucmFkbGVyQHBieC5hdCIsImdpdmVuX25hbWUiOiJEb21pbmlrIiwiZmFtaWx5X25hbWUiOiJSYWRsZXIiLCJlbWFpbCI6ImRvbWluaWsucmFkbGVyQHBieC5hdCJ9.jp-LmDoHvGvWMZEcnKfIWJ17E2c5LY5U1SZHJ7h5wD5XCHmT6-ky3BQS0Urj2HIfN_TsdOjHrz08mtidPgTttMXXrnRvDHiEde-sZLh1fau6XQynpU68WNF77BvGhMGTK0MUufcISBdoaY1mE353ff1WPDdB2ullDCCDFyr1jq0KLRiTnEqVFTGkkIrouh5kNBg5VTkTs0km0icsSXw1Y9MuaJtglPB5WODdjjXYzNHSPPJHCt-bMhwdvoemdAtnsWsWBMNAN9pvd6S0bNI3eoIDVt6wiOFXm3CHee5orILw3f-0vdgqKco0DRBCrRX9QvX5TGu_1tbjqLVbNZFKmw'
api_header = {'Authorization': 'Bearer '+access_token}


resp = requests.get(url=url+"/api/auth/v1/companies", headers=api_header)
print(resp.json())

company_id = "494"

# resp = requests.patch(url=url+"/api/erp/v1/part/000333/cost", headers={'Authorization': 'Bearer '+access_token, 'itemNumber': "000333", 'upc-selected-company': company_id})
# print(resp.json())
resp = requests.patch(
    url=url+"/api/bom/v1/part_number/800492/exists",
    headers={'Authorization': 'Bearer '+access_token,
             'itemNumber': "000330",
             'upc-selected-company': company_id}
)

print(resp.json())
