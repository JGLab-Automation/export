import json
import mimetypes
import os
import subprocess
import sys
import tarfile
import time

import requests
from requests.auth import HTTPBasicAuth

USERNAME=os.getenv("USERNAME")
PASSWORD=os.getenv("PASSWORD")
NAMESPACE=os.getenv("NAMESPACE")
CASSERVER=f"cas.{NAMESPACE}.svc.cluster.local"
SERVER=f"https://{CASSERVER}:28809"


def download_exp_from_git(url):
    local_filename = "exp.tar.gz"

    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(local_filename, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        print(f"Downloaded {local_filename}")
    else:
        print("Error:", response.status_code, response.text)

def extract_tar_gz(file_path, extract_path):
    try:
        with tarfile.open(file_path, 'r:gz') as tar:
            tar.extractall(path=extract_path)
            print(f"Extracted '{file_path}' to '{extract_path}'")
    except Exception as e:
        print(f"Error extracting file: {e}")
    finally:
        os.remove(file_path)

# def get_pod_name(namespace):  
#     pass

# def copy_file_between_pods(file_path, dest_path, namespace="sdlcdt11"):
#     dest_pod = get_pod_name(namespace=namespace)
#     try:
#         subprocess.run(["kubectl", "cp", file_path, f"{namespace}/{dest_pod}:{dest_path}"], check=True)

#         print("File copied successfully!")

#     except subprocess.CalledProcessError as e:
#         print(f"Error: {e}")

def get_files(directory):
    files = os.listdir(directory)
    print(files)

def get_fileType(file_path):
    mime_type, _ = mimetypes.guess_type(file_path)
    print(mime_type)

def get_fileName(file_path):
    file_name = os.path.basename(file_path)
    return file_name.split(".tar")[0]

def read_exp_content(file_path):
    with open(file_path, "r") as file:
        data = json.load(file)
    return data

def get_transaction_id(payload):
    url = f"{SERVER}/restconf/operations/nokia-sdl:load-exp"

    response = requests.post(url, json=payload, auth=HTTPBasicAuth(USERNAME, PASSWORD))
    if response.status_code == 201:
        data = response.json()
        transaction_id = data.get("nokia-sdl:output").get("transaction-id")
        return transaction_id
    else:
        print("Error:", response.status_code, response.text)

    # Test output
    #     data = {
    #   "nokia-sdl:output": {
    #     "transaction-id": "d37531fd-2025-4bc6-8f8d-520b4ab6d90e"
    #   }
    # }
    #     transaction_id = data.get("nokia-sdl:output").get("transaction-id")
    #     return transaction_id

def get_transaction_status(txn_id):
    url = f"{SERVER}/restconf/data/nokia-sdl:sdl/state/derived-state/deployments/deployment=1/vnf-instances/vnf-instance=sdlcdt11/operation/transactions/transaction={txn_id}"
    count = 0
    while count == 10:
        response = requests.get(url, auth=HTTPBasicAuth(USERNAME, PASSWORD))
        if response.status_code == 200:
            data = response.json()
            txn_status = data.get("nokia-sdl:transaction").get("status")
            if txn_status == "SUCCESS":
                return "success"
            else:
                time.sleep(5)
                count += 1
        else:
            print("Error:", response.status_code, response.text)
            return "error"

def get_extension_package_payload(expected_status):
    url = f"{SERVER}/restconf/data/nokia-sdl:sdl/state/derived-state/deployments/deployment=1/vnf-instances/vnf-instance=sdlcdt11/extensions/extension-packages"
    response = requests.get(url, auth=HTTPBasicAuth(USERNAME, PASSWORD))
    if response.status_code == 200:
        data = response.json()
        ext_pkgs = data.get("nokia-sdl:extension-packages")
        for pkg in ext_pkgs:
            if pkg.get("name") == "sdla":
                if pkg.get("status").lower() == expected_status:
                    if expected_status == "activated":
                        return
                    pkg.pop("status")
                    payload = {"input":{"extension-packages":[pkg]}}
                    return payload
            else:
                print("Package not found")
    else:
        print("Error:", response.status_code, response.text)  

def prepare_extension_package(payload):
    url = f"{SERVER}/restconf/operations/nokia-sdl:prepare-exp"
    response = requests.post(url, json=payload, auth=HTTPBasicAuth(USERNAME, PASSWORD))
    if response.status_code == 201:
        data = response.json()
        transaction_id = data.get("nokia-sdl:output").get("transaction-id")
        return transaction_id
    else:
        print("Error:", response.status_code, response.text)

def activate_extension_package(payload):
    url = f"{SERVER}/restconf/operations/nokia-sdl:activate-exp"
    response = requests.post(url, json=payload, auth=HTTPBasicAuth(USERNAME, PASSWORD))
    if response.status_code == 201:
        data = response.json()
        transaction_id = data.get("nokia-sdl:output").get("transaction-id")
        return transaction_id
    else:
        print("Error:", response.status_code, response.text)


if __name__=='__main__':
    filePath = "C:\\Users\\JG\\Documents\\DT\\Onyx\\service_primitive\\SDL-SDLA-23.11.0-1-WX-ExP.tar"
    extractPath = "C:\\Users\\JG\\Documents\\DT\\Onyx\\service_primitive\\SDL"
    repo_path = https://git/exp.tar.gz

    download_exp_from_git(url=repo_path)
    extract_tar_gz(file_path=filePath, extract_path=extractPath)
    file_name = get_fileName(file_path=filePath)
    exp_json_file_path = f"{extractPath}\\{file_name}.json"
    payload = read_exp_content(file_path=exp_json_file_path)
    txn_id = get_transaction_id(payload=payload)
    txn_status = get_transaction_status(txn_id=txn_id)
    if txn_status == "success":
        ext_pkg_payload = get_extension_package_payload(expected_status="new")
        ext_pkg_txn_id = prepare_extension_package(payload=ext_pkg_payload)
        ext_pkg_txn_status = get_transaction_status(txn_id=ext_pkg_txn_id)
        if ext_pkg_txn_status == "success":
            ext_pkg_payload = get_extension_package_payload(expected_status="deactivated")
            activate_ext_pkg_txn_id = activate_extension_package(payload=ext_pkg_payload)
            activate_ext_pkg_txn_status = get_transaction_status(txn_id=activate_ext_pkg_txn_id)
            _ = get_extension_package_payload(expected_status="activated")
        else:
            print(f"Transaction status: {txn_status}")
            sys.exit(2)            
    else:
        print(f"Transaction status: {txn_status}")
        sys.exit(1)
