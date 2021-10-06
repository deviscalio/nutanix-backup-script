import hashlib
import json
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
from datetime import datetime
import sys
import click
import glob
import os

@click.group()
def cli():
    pass

def clean_backup_folder():
    for vm in cfg["vms"]:
        files = list(sorted(glob.iglob(cfg["config"]["download_path"] + "\\*" + vm["name"] + "*")))
        while len(files) > vm["keep"]:
            print("Delete file " + files[0])
            os.remove(files[0])
            files.remove(files[0])

def delete_ova(ova_uuid):
    headers = {
        "content-type": "application/json",
        "authorization": "Basic " + cfg["config"]["authorization_key"]
        }
    url = "https://trr-prism-ap2:9440/api/nutanix/v3/ovas/" + ova_uuid
    response = requests.request("DELETE", url, headers=headers, verify=False)
    print(response.text)

def download_ova(vm_name,ova_name,ova_uuid,filehash,backup_path):
    print("Download " + ova_name)
    url = "https://trr-prism-ap2:9440/api/nutanix/v3/ovas/" + ova_uuid + "/file"
    headers = {
        "content-type": "application/json",
        "authorization": "Basic " + cfg["config"]["authorization_key"]
        }
    response = requests.request("GET", url, headers=headers, verify=False)

    filename = backup_path + vm_name + "-" + ova_name + ".ova"
    file_ = open(filename, 'wb')
    file_.write(response.content)
    file_.close()

    print(ova_name + " downloaded")

    filehash_downloaded = hashlib.sha256(open(filename,'rb').read()).hexdigest();
    if filehash == filehash_downloaded:
        delete_ova(ova_uuid);
    else:
        print("Error to get OVA " + ova_name)
        os._exit(1)

def get_all_ova(backup_path):
    payload = "{\"kind\":\"ova\"}"
    url = "https://trr-prism-ap2:9440/api/nutanix/v3/ovas/list"
    headers = {
        "content-type": "application/json",
        "authorization": "Basic "+ cfg["config"]["authorization_key"]
        }
    response = requests.request("POST", url, data=payload, headers=headers, verify=False)
    ovas = json.loads(response.text)
    if len(ovas["entities"]):
        for ova in ovas["entities"]:
            vm_name = (ova["info"]["parent_vm_reference"]["name"])
            ova_uuid = (ova["metadata"]["uuid"])
            ova_name = (ova["info"]["name"])
            filehash = (ova["info"]["checksum"]["checksum_value"])
            download_ova(vm_name,ova_name,ova_uuid,filehash,backup_path)
        clean_backup_folder()
    else:
        print("No OVA to download.")


def create_ova(vm_name,vm_uuid):
    now = datetime.now() # current date and time
    date_string = now.strftime("%Y%m%d-%H%M%S")
    payload = {
        "name": vm_name + "-" + date_string,
        "disk_file_format": "VMDK"
    }
    payload_json = json.dumps(payload)
    headers = {
        "content-type": "application/json",
        "authorization": "Basic " + cfg["config"]["authorization_key"]
        }
    url = "https://trr-prism-ap2:9440/api/nutanix/v3/vms/" + vm_uuid +"/export"
    print("Create task to create OVA for VM " + vm_name)
    response = requests.request("POST", url, data=payload_json, headers=headers, verify=False)
    print(response.text)

def can_backup(period):
    now = datetime.now()
    day = now.strftime("%w")
    if period == "daily":
        return True
    elif period == "weekdays":
        if int(day) >= 1 and int(day) <=5:
            return True,
    elif "weekly":
        if int(day) == 5:
            return True
    else:
      return False

@cli.command(help="Create Ova for VM to backup")
def backup():
    for vm in cfg["vms"]:
        if can_backup(vm["period"]):
            create_ova(vm["name"],vm["uuid"])

@cli.command(help="Download and delete Ova from Nutanix to Download Folder")
def get():
    get_all_ova(cfg["config"]["download_path"])

@cli.command(help="Test config file after editing")
def test_config():
    print("Config file OK")

if __name__ == '__main__':
    try:
        with open("nutanix-backup.json", "r") as config_file:
            cfg = json.load(config_file)
    except Exception as e:
        print("Error Message: " + str(e))
        os._exit(1)
    cli()
