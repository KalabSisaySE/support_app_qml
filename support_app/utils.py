import ctypes
import psutil
import requests
import socket
import webbrowser


def get_process_command_lines(process_name):
    try:
        command_lines = []
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            if proc.info['name'] and proc.info['name'].lower() == process_name.lower():
                cmdline = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
                print(f"\n\t\t\tcmdline: {cmdline}")
                command_lines.append(cmdline)
        print(f"\n\t\t\tcmdline over")
        return command_lines
    except Exception as e:
        return []


def is_app_running():
    """
    Check if a Macrosoft Remote Desktop is running.
    :return: True if the process is running, False otherwise.
    """
    process_name = "macrosoftconnectquicksupport.exe"

    for proc in psutil.process_iter(['name']):
        try:
            if proc.info['name'] and process_name.lower() == proc.info['name'].lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False

def is_service_running(service_name):
    try:
        service = psutil.win_service_get(service_name)
        return service.status() == 'running'
    except psutil.NoSuchProcess:
        return False
    except Exception as e:
        return False


def get_full_name(access):
    import requests
    if access:
        url = f'https://online.macrosoft.sk/rustdesk/username/?access={access}'
        try:
            res = requests.get(url)

            json_data = res.json()
            if json_data.get('status') == 'found':
                return json_data.get('full_name', 'Neznáme meno')
            else:
                return 'Neznáme meno'

        except Exception as e:
            return

def open_website(access):
    if access:
        url = f'https://online.macrosoft.sk/online/?access={access}'
        webbrowser.open(url)
        return True
    else:
        return False


def is_user_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def get_local_ip():
    hostname = socket.gethostname()
    return socket.gethostbyname(hostname)

def get_public_ip():
    try:
        return requests.get("https://api64.ipify.org?format=text").text
    except requests.RequestException:
        return


def get_latest_access_code():
    try:
        my_ip = get_public_ip()
        if my_ip:
            url = "https://online.macrosoft.sk/get/lectoure/access/"
            res = requests.post(url, json={"ip_address": my_ip})

            if res.status_code == 200:
                return res.json().get('access_code', "")
        else:
            return ""
    except:
        return ""

