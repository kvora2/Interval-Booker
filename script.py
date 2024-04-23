import time
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from twilio.rest import Client

current_hour = datetime.now().hour
current_minute = datetime.now().minute

print("Hour:", current_hour)
print("Minute:", current_minute)


# Set up Twilio credentials
twilio_account_sid = 'ACaf518c3a1c148f9519c75a8c06fbbb04'
twilio_auth_token = 'b2c3097507f9628e7fc57aa6a68c9414'
twilio_phone_number = '9592148015'
recipient_phone_number = '4379710121'


# the week that user wants to book intervals for...2 for current one, 3 for next week and so on..
week = 2

# Send the SMS notification using
client = Client(twilio_account_sid, twilio_auth_token)

weekdays = {
    "2": "Sunday",
    "3": "Monday",
    "4": "Tuesday",
    "5": "Wednesday",
    "6": "Thursday",
    "7": "Friday",
    "8": "Saturday"
}

options = Options()
options.binary_location = "/Applications/Firefox.app/Contents/MacOS/firefox-bin"
driver = webdriver.Firefox(options=options)
DAYS = 7
SLOTS = 48


def login():
    desired_url = "https://register.arise.com/opportunities"
    driver.get(desired_url)

    # Get the current URL
    current_url = driver.current_url

    if desired_url != current_url:
        # enter the username
        username = driver.find_element(By.ID, 'username')
        username.send_keys('KelvinV')

        # enter pwrd
        pwd = driver.find_element(By.ID, 'pwd')
        pwd.send_keys('Charmi@1234')

        submit = driver.find_element(By.CLASS_NAME, 'login-btn-2')
        submit.click()

# Open starmatics via 'Portal'
def openStarmatics():
    driver.get('https://link.arise.com/home')

    time.sleep(5)

    starmatic = driver.find_element(
        By.XPATH, "//span[contains(text(), 'Starmatic')]")
    starmatic.click()

    time.sleep(2)

    driver.get(
        'https://starmatic.arise.com/Starmatic/Pages/Acp/QuickPost/ScheduleReleases.aspx')

    # If in case there is any extra tab. switch and close it
    if (len(driver.window_handles) > 1):
        driver.switch_to.window(driver.window_handles[1])
        driver.close()

    driver.switch_to.window(driver.window_handles[0])
    time.sleep(1)
    # 2 for this week and 3 for next week and so on..
    button = driver.find_element(
        By.ID, f'ctl00_cphMain_gdvSchdRel_ctl0{week}_lnkSchTyp')
    button.click()

# Open starmatics via 'Client Opportunities'
def openStarmatics1():
    myPrograms = driver.find_element(
        By.XPATH, "//a[contains(text(), 'My Programs')]")
    myPrograms.click()

    starmatic = driver.find_element(
        By.XPATH, "//span[contains(text(), 'Starmatic')]")
    starmatic.click()

    time.sleep(8)

    driver.get(
        'https://starmatic.arise.com/Starmatic/Pages/Acp/QuickPost/ScheduleReleases.aspx')

    # If in case there is any extra tab. switch and close it
    if (len(driver.window_handles) > 1):
        driver.switch_to.window(driver.window_handles[1])
        driver.close()

    driver.switch_to.window(driver.window_handles[0])
    time.sleep(1)
    # 2 for this week and 3 for next week and so on..
    button = driver.find_element(
        By.ID, f'ctl00_cphMain_gdvSchdRel_ctl0{week}_lnkSchTyp')
    button.click()


# logging in
login()

time.sleep(2)
closeButton = driver.find_element(By.CLASS_NAME, 'close')
closeButton.click()
time.sleep(2)
# open starmatics and particular week
openStarmatics()

while True:
    try:
        check = False
        # getting current time
        curr_hour = datetime.now().hour
        curr_minute = datetime.now().minute

        # in case session times out, it will give an exception and will start a new session
        error = ""
        try:
            error = driver.find_element(
                By.XPATH, "//span[contains(text(), 'Error')]")
        except:
            pass

        if error != "":
            raise Exception("request time out!!")

        # getting all the available slots that are also unchecked
        openSlots = driver.find_elements(
            By.XPATH, "//input[@type='checkbox' and not(@disabled) and not(@checked)]")
        Msg = ""

        for slot in openSlots:
            slotId = slot.get_attribute("id")
            slotDay = slotId[41:42]
            slotTime = slotId[-2:]
            slotDayMsg = weekdays.get(slotDay)
            slotTimeMsg = (int(slotTime)-1)/2
            Msg += "{} : {}\n".format(slotDayMsg, slotTimeMsg)

            if ((slotDayMsg == "Tuesday") and ((slotTimeMsg >= 6 and slotTimeMsg <= 11.5))):
                driver.find_element(By.ID, f"{slotId}").click()
                check = True
            # if ((slotDayMsg == "Saturday") and ((slotTimeMsg >= 6 and slotTimeMsg <= 12))):
            #     driver.find_element(By.ID, f"{slotId}").click()
            #     check = True

        # will check if there are intervals selected and than submit
        if check:
            driver.find_element(By.ID, 'ctl00_cphMain_btnSubmit').click()
            driver.find_element(By.ID, 'btnAlertOK').click()
            driver.get('https://starmatic.arise.com/Starmatic/Pages/Acp/QuickPost/ScheduleReleases.aspx')
            driver.find_element(By.ID, f'ctl00_cphMain_gdvSchdRel_ctl0{week}_lnkSchTyp').click()
            # Send msg
            message = client.messages.create(
                body = Msg,
                from_ = twilio_phone_number,
                to = recipient_phone_number
            )
            print(f"SMS sent! Message : {message.body}")
        # else:
        #     # If there is any msg than send it to me
        #     if Msg != "":
        #         ## Send msg
        #         message = client.messages.create (
        #                     body = Msg,
        #                     from_ = twilio_phone_number,
        #                     to = recipient_phone_number
        #         )
        #         print(f"SMS sent! Message : {message.body}")

        time.sleep(1)
        driver.refresh()
    except:
        print("exception occured!!")
        ## logging in
        login()

        time.sleep(4)

        # open starmatics and particular week
        openStarmatics()
