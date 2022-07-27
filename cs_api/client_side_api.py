import os
import io
import json
import requests
import pandas as pd
from urllib.parse import unquote

from typing import Union


def get_method(url: str, access_token: str = None):
    token = access_token

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    response = requests.get(url=url, headers=headers)
    if response.status_code == 200:
        text = json.loads(response.text)
        # print response text
        print(json.dumps(text, indent=2))
        return text
    else:
        print(f"Error: {response.status_code} {response.reason}")


def post_method(url: str, access_token: str = None, body: dict = None):
    token = access_token

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    response = requests.post(url=url, json=body, headers=headers)
    if response.status_code == 200:
        text = json.loads(response.text)

        # print response text
        print(json.dumps(text, indent=2))

        return text
    else:
        text = json.loads(response.text)
        print(f"Error: {response.status_code} {response.reason}")
        # print response text
        print(json.dumps(text, indent=2))


def get_auth_token(base_url: str, access_token: str):
    auth_path = "auth/test-token"
    auth_url = base_url + auth_path

    get_method(url=auth_url, access_token=access_token)


def get_dataset(base_url: str, access_token: str):
    dataset_path = "datasets/"
    dataset_url = base_url + dataset_path

    get_method(url=dataset_url, access_token=access_token)


def get_users(base_url: str, access_token: str):
    users_path = "users/"
    users_url = base_url + users_path

    get_method(url=users_url, access_token=access_token)


def post_create_dataset(base_url: str, dataset: dict, access_token: str):
    dataset_path = "datasets/"
    dataset_url = base_url + dataset_path

    params = post_method(url=dataset_url, body=dataset, access_token=access_token)

    return params


def post_create_model(base_url: str, model: dict, access_token: str):
    model_path = "models/"
    model_url = base_url + model_path

    params = post_method(url=model_url, body=model, access_token=access_token)

    return params


def get_optimize_model(base_url: str, output: str, model_id: int, access_token: str):
    opt_path = f"models/{model_id}/optimize"
    params = f"?output={output}"
    opt_url = base_url + opt_path + params

    print("*** Optimize Model ***")
    token = access_token

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    response = requests.get(url=opt_url, headers=headers)
    if response.status_code == 200:
        dir_output = os.path.join(os.path.dirname(__file__), "../output")
        if not os.path.exists(dir_output):
            os.mkdir(dir_output)
        try:
            url_filename = response.headers["content-disposition"].split("''")[1].strip()
        except:
            url_filename = response.headers["content-disposition"].split('"')[1].strip()
        filename = os.path.join(dir_output, unquote(url_filename))
        g = io.BytesIO(response.content)
        with open(filename, mode='wb') as out:
            out.write(g.read())
            print("*** Output file created ***")
        return filename
    else:
        print(f"Error: {response.status_code} {response.reason}")
    print("*** Optimize Model Done ***")


def post_upload_zip(base_url: str, data: str, dataset_id: int, access_token: str):
    upload_path = f"datasets/{dataset_id}/upload"
    upload_url = base_url + upload_path

    token = access_token

    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {token}",
    }
    opened_file = open(data, 'rb')
    files = {
        'file': (opened_file.name, opened_file, "application/x-zip-compressed")
    }

    response = requests.post(url=upload_url, files=files, headers=headers)
    if response.status_code == 200:
        text = json.loads(response.text)

        # print response text
        print(json.dumps(text, indent=2))

        return text
    else:
        text = json.loads(response.text)
        print(f"Error: {response.status_code} {response.reason}")
        # print response text
        print(json.dumps(text, indent=2))
        return -1


def post_register(base_url: str, body: dict, access_token: Union[str, None] = None):
    register_path = "auth/register"
    register_url = base_url + register_path

    post_method(url=register_url, body=body, access_token=access_token)


def post_login(base_url: str, account: dict):
    login_path = "auth/login"
    login_url = base_url + login_path

    username, password = account.values()
    # Write parameter with x-www-form-urlencoded format
    params = f"username={username}&password={password}"
    # Write parameter with json format, both of them works
    dict_params = {'username': 'felixarjuna', 'password': 'password'}

    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    response = requests.post(url=login_url, data=params, headers=headers)

    print("*** Login in ... ***")
    text = json.loads(response.text)
    if response.status_code == 200:
        access_token, token_type = text.values()
        print(json.dumps(text, indent=2))
        print("*** Login successful! :) ***")
        return access_token
    else:
        print("*** Login failed ! :( ***")
        text = json.loads(response.text)
        print(f"Error: {response.status_code} {response.reason}")
        # print response text
        print(json.dumps(text, indent=2))


def get_reset_database(base_url: str):
    reset_path = "reset"
    reset_url = base_url + reset_path

    response = get_method(url=reset_url)

    return response


def generate_template():
    template_account = {"username": None,
                        "password": None}

    template_dataset = {"name": None, "description": None, "hours_per_time_step": 1, "number_of_time_steps": 35040,
                        "cost_unit": "1e6 €", "length_unit": "km", "ref_created_by": 0}

    template_model = {
        "name": "100 CO2 reduction",
        "description": "A model that reduces CO2 emissions by 100%",
        "ref_dataset": 1,
        "parameters": []
    }

    return template_account, template_dataset, template_model

# Links
# Convert URL String to Normal String
# https://stackoverflow.com/questions/11768070/transform-url-string-into-normal-string-in-python-20-to-space-etc

# How to store bytes to Excel File
# https://stackoverflow.com/questions/66831249/how-to-store-bytes-like-bpk-x03-x04-x14-x00-x08-x08-x08-x009bwr-x00-x00-x00-x00

# Common MIME types
# https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types/Common_types

# HTTP Response Status Code
# https://developer.mozilla.org/en-US/docs/Web/HTTP/Status#client_error_responses

# Convert BytesIO into File
# https://python.tutorialink.com/convert-bytesio-into-file/

# Curl command converter
# https://curlconverter.com/

# Set attribute to object
# https://stackoverflow.com/questions/2827623/how-can-i-create-an-object-and-add-attributes-to-it

# How to UploadFile using FastAPI
# https://stackoverflow.com/questions/63048825/how-to-upload-file-using-fastapi/70657621#70657621
