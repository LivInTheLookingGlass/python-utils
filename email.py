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

    server = smtplib.SMTP(*SERVER)
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

    print to

    sendMail(text, "Phone alert", to, SERVER=SERVER,
             ADDRESS=ADDRESS, PSWD=PSWD)


def parseCarriers(to, carrier):
    """Parse the email address of a given number and carrier"""
    if carrier == "Alltel":
        return str(to) + "@sms.alltelwireless.com"
    elif carrier == "AT&T":
        return str(to) + "@txt.att.net"
    elif carrier == "Bell Canada":
        return str(to) + "@txt.bellmobility.ca"
    elif carrier == "Boost":
        return str(to) + "@sms.myboostmobile.com"
    elif carrier == "Centennial":
        return str(to) + "@cwemail.com"
    elif carrier == "Cellular South":
        return str(to) + "@csouth1.com"
    elif carrier == "Cincinnati Bell":
        return str(to) + "@gocbw.com"
    elif carrier == "Cricket":
        return str(to) + "@sms.mycricket.com"
    elif carrier == "Metro PCS":
        return str(to) + "@metropcs.sms.us"
    elif carrier == "Qwest":
        return str(to) + "@qwestmp.com"
    elif carrier == "Rogers":
        return str(to) + "@pcs.rogers.com"
    elif carrier == "Sprint":
        return str(to) + "@messaging.sprintpcs.com"
    elif carrier == "Suncom":
        return str(to) + "@tms.suncom.com"
    elif carrier == "T-Mobile":
        return str(to) + "@tmomail.net"
    elif carrier == "Telus":
        return str(to) + "@msg.telus.com"
    elif carrier == "US Cellular":
        return str(to) + "@email.uscc.net"
    elif carrier == "Verizon":
        return str(to) + "@vzwpix.com"
    else:  # elif carrier == "Virgin":
        return str(to) + "@vmobl.com"
