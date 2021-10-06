## Description
This script helps you to manage OVAs on Nutanix AHV. This script invokes API of Prism Central to make OVAs of VM and get them to put in a remote folder.

## How To Use

To clone and run this application, you'll need [Git](https://git-scm.com) and [Python](https://www.python.org/) installed on your computer. From your command line:

```powershell
# Install python libraries
C:\> pip install click
C:\> pip install requests

# Clone this repository
C:\> git clone https://github.com/deviscalio/nutanix-backup-script.git

# Go into the repository
C:\> cd nutanix-backup-script

# Edit the json config file
C:\> notepad nutanix-backup.json

# run help
C:\> nutanix-backup-script> nutanix-backup.py --help

```

Note: This script is tested using Windows.

## Config file
```json
{
  "vms": [
    {
        "name": "",
        "uuid": "",
        "period": "",
        "keep": 2
    }
  ],
  "config": {
    "download_path": "< put here the path >",
    "authorization_key": "< put here the authorization_key >"
  }
}
```
* **name** (Name of virtual machine)
* **uuid** (UUID of virtual machine. You can get it from Prism Element)
* **period** (Available periods are: dayly, weekdays, weekly)
* **keep** (Number of OVA to keep)
