from twilio.rest import Client

#--------------------------------------------------------
# change values of account_sid, auth_token, to and from - all from twilio account

def send(value, classes):
    # Your Account SID from twilio.com/console
    account_sid = "AC003b9acfef131e7978b5f9c451a1107c"
    # Your Auth Token from twilio.com/console
    auth_token  = "e15031a2ee99f4e96abaf2724ce96a0c"

    client = Client(account_sid, auth_token)

    message = client.messages.create(
        to="+918523076819",
        from_="+18653906029",
        body=f"Blindness detection system report! severity level is : {value} and class is {classes}")
    print('Message sent Succesfully !')
    print(message.sid)
