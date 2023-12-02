import requests


def interact_code_llm(text, token, custom_llm_server_token):

    headers = {
        'accept': 'application/json',
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
    }
    
    data = f'{{ "text": "{text}" }} '

    response = requests.post(f'{custom_llm_server_token}/predict/', headers=headers, data=data)
    return response.json()

