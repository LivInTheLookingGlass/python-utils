def sendMail(text, subject, to, SERVER=("localhost"),
             ADDRESS="sender@example.com", PSWD="test"):
    """Sends an email from a defined smtp server"""
    import smtplib

    message = """\
    From: %s
    To: %s
    Subject: %s

    %s
    """ % (ADDRESS, ", ".join(to), subject, text)

    # Send the mail

    server = smtplib.SMTP(SERVER)
    if SERVER != "localhost":
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(ADDRESS, PSWD)
    server.sendmail(ADDRESS, to, message)
    server.quit()


def sendText(text, to, carriers, SERVER="localhost",
             ADDRESS="sender@example.com", PSWD="test"):
    """Sends a text message to a number on supported carriers"""
    for i in range(len(to)):
        to[i] = parseCarriers(to[i], carriers[i])

    print(to)

    sendMail(text, "Phone alert", to, SERVER=SERVER,
             ADDRESS=ADDRESS, PSWD=PSWD)


def parseCarriers(to, carrier):
    """Parse the email address of a given number and carrier"""
    carriers = {"Alltel": "@sms.alltelwireless.com",
                "AT&T": "@txt.att.net",
                "ATT": "@txt.att.net",
                "Bell Canada": "@txt.bellmobility.ca",
                "Boost": "@sms.myboostmobile.com",
                "Centennial": "@cwemail.com",
                "Cellular South": "@csouth1.com",
                "Cincinnati Bell": "@gocbw.com",
                "Cricket": "@sms.mycricket.com",
                "Metro PCS": "@metropcs.sms.us",
                "Qwest": "@qwestmp.com",
                "Rogers": "@pcs.rogers.com",
                "Sprint": "@messaging.sprintpcs.com",
                "Suncom": "@tms.suncom.com",
                "T-Mobile": "@tmomail.net",
                "Telus": "@msg.telus.com",
                "US Cellular": "@email.uscc.net",
                "Verizon": "@vzwpix.com"}
    if carrier in carriers:
        return str(to) + carriers[carrier]
    else:  # elif carrier == "Virgin":
        return str(to) + "@vmobl.com"
