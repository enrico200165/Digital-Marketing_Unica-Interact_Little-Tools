
from locust import HttpLocust, TaskSet, task


# ----- tasks -----


# ----- task sets ----

class WebSession01TS(TaskSet):

    # def on_start(self):
    #     pass
    #
    # def on_stop(self):
    #     pass
    @task
    def startUACISession(self):
        print("startSession")
        # l.client.post("/login", {"username":"ellen_key", "password":"education"})


class WebSession01(HttpLocust):
    def __init__(self):
        s = super()
        print(s)
        print("ok")
        self.host = "http://example.com"
        super().__init__()

    task_set = WebSession01TS

# cd C:\Users\e_viali\Documents\dev\intellij\MarketingCloudLittleTools\InteractRESTBasicAPITest\stress_test
# locust --host=http://   --master -f locust_session01.py

# cd C:\Users\e_viali\Documents\dev\intellij\MarketingCloudLittleTools\InteractRESTBasicAPITest\stress_test
# locust --host=http:// --slave -f locust_session01.py
