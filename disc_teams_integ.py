import json
from discoIPC import ipc
import configparser
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import time
import atexit


def init_important():
    config = configparser.ConfigParser()
    config.read('config.ini')
    _client = ipc.DiscordIPC(config['CLIENT']['client_id'])
    installer = ChromeDriverManager().install()
    options = Options()
    options.headless = True
    _driver = webdriver.Chrome(installer, options=options)
    _driver.get('https://developer.microsoft.com/en-us/graph/graph-explorer')
    _driver.find_element_by_xpath('/html/body/div[4]/div/div[2]/div[1]/div[2]/div[1]/div/button/span').click()
    _driver.switch_to.window(_driver.window_handles[1])
    _driver.implicitly_wait(5)
    _driver.find_element_by_xpath(
        '/html/body/div/form[1]/div/div/div[2]/div/div/div[1]/div[2]/div[2]/div/div/div/div[2]/div[2]/div/input[1]').send_keys(
        'org_email')
    _driver.find_element_by_xpath(
        '/html/body/div/form[1]/div/div/div[2]/div/div/div[1]/div[2]/div[2]/div/div/div/div[4]/div/div/div/div[2]/input').click()
    _driver.find_element_by_xpath('/html/body/div/div[2]/div/form/div[3]/input').send_keys('org_username')
    _driver.find_element_by_xpath('/html/body/div/div[2]/div/form/div[5]/input').send_keys('org_password')
    _driver.find_element_by_xpath('/html/body/div/div[2]/div/form/div[6]/a').click()
    time.sleep(15)
    _driver.switch_to.window(_driver.window_handles[0])
    time.sleep(3)
    return [_client, _driver]


def get_new_access_token():
    driver.find_element_by_xpath(
        '/html/body/div[4]/div/div[2]/div[2]/div[1]/div[2]/div/div/div[1]/div[1]/button[4]/span/div').click()
    driver.implicitly_wait(5)
    access_token = driver.find_element_by_xpath(
        '/html/body/div[4]/div/div[2]/div[2]/div[1]/div[2]/div/div/div[1]/div[2]/div/div/div/div/div/label').text
    f = open("../ACCESS_TOKEN.txt", "w")
    f.write(access_token)
    f.close()


def read_file():
    file = open('../REQUEST_OUTPUT.txt', 'r')
    request_info = file.read()
    file.close()
    parts = request_info.split('\n')
    status = parts[0]
    if status != '200' or int(time.time()) - start_time > 3555:
        get_new_access_token()
        return -1
    response = parts[1]
    j_resp = json.loads(response)
    availability = j_resp['availability']
    activity = j_resp['activity']
    return [availability, activity]


def map_availability_and_activity(avail, act):
    avail_mappings = {
        "Available": "AVAILABLE",
        "AvailableIdle": "AVAILABLE IDLE",
        "Away": "AWAY",
        "BeRightBack": "BE RIGHT BACK",
        "Busy": "BUSY",
        "BusyIdle": "BUSY IDLE",
        "DoNotDisturb": "DO NOT DISTURB",
        "Offline": "OFFLINE",
        "PresenceUnknown": "PRESENCE UNKNOWN"
    }

    act_mappings = {
        "Available": "AVAILABLE",
        "BeRightBack": "BE RIGHT BACK",
        "Busy": "BUSY",
        "DoNotDisturb": "DO NOT DISTURB",
        "InACall": "IN A CALL",
        "InAConferenceCall": "IN A CONFERENCE CALL",
        "Inactive": "INACTIVE",
        "InAMeeting": "IN A MEETING",
        "Offline": "OFFLINE",
        "OffWork": "OFF WORK",
        "OutOfOffice": "OUT OF OFFICE",
        "PresenceUnknown": "PRESENCE UNKNOWN",
        "Presenting": "PRESENTING",
        "UrgentInterruptionsOnly": "URGENT INTERRUPTIONS ONLY"
    }

    return [avail_mappings[avail], act_mappings[act]]


def check():
    rp = {
        'timestamps': {},
        'assets': {
            'large_image': 'ms_teams_logo',
            'large_text': 'Teams'
        }
    }

    client.connect()

    time_elapsed = int(time.time())

    def set_activity(state, details):
        rp['state'] = state
        rp['details'] = details
        rp['timestamps']['start'] = time_elapsed
        return rp

    get_avail_act = read_file()
    if get_avail_act == -1:
        return
    availability = get_avail_act[0]
    if availability == 'Offline':
        return -1
    activity = get_avail_act[1]
    important_acts = {'InACall', 'InAMeeting', 'Presenting', 'InAConferenceCall'}
    while activity in important_acts:
        map_avail_act = map_availability_and_activity(availability, activity)
        set_activity(map_avail_act[0], map_avail_act[1])
        client.update_activity(rp)
        file = open('../REQUEST_OUTPUT.txt', 'r')
        request_info = file.read()
        file.close()
        parts = request_info.split('\n')
        if parts[0] != '200':
            client.disconnect()
            break
        response = parts[1]
        j_resp = json.loads(response)
        activity = j_resp['activity']
    else:
        client.disconnect()


important_vars = init_important()
client = important_vars[0]
driver = important_vars[1]
get_new_access_token()
start_time = int(time.time())
while True:
    if check() == -1:
        print('Offline.')
        break
    time.sleep(5)


@atexit.register
def close():
    driver.close()
    driver.quit()
    client.disconnect()
