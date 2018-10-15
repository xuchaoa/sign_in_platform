import datetime
import requests

class APIC:
    def encode(self, text=str(datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"))):
        if self.token and self.key and text:
            from itertools import cycle
            result=''
            temp=cycle(self.key)
            for x in text:
                result=result+"%02x" % (ord(x) ^ ord(next(temp)))
            return result
        else:
            return None

    def send(self):
        if self.token and self.key and self.data:
            self.data = self.encode(datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"))
            post_data = dict(token=self.token, data=self.data)
            try:
                r = requests.post(url=self.url, data=post_data)
                if r.text == "\"OK\"":
                    return True
                else:
                    return False
            except Exception as e:
                return e
        return False


    def __init__(self, token="407b5a42-e094-5942-b150-816160124e17", key="d90beae9-3a45-53da-8138-b4194110b8d1", ip="checker.507.sec", port="80"):
        self.token = token
        self.key = key
        self.data = self.encode(datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"))
        self.url = "http://%s:%s/sdk/token" % (ip, port)



