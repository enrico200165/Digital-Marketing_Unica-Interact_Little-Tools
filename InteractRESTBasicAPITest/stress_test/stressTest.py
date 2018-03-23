'''
Locust file
-----------
A locustfile is a normal python file.
The only requirement is that it declares at least one class —
let’s call it the locust class— that inherits from the class Locust.

You can run two locusts from the same file like so:
locust -f locust_file.py WebUserLocust MobileUserLocust
(WebUserLocust MobileUserLocust are names of locust classes
contained in the file)


Locust class
-----------
represents one user (or a swarming locust if you will).
Locust will spawn (hatch) one instance of the locust class
for each user that is being simulated.
??? how do I set how many user and how they are identified

There are a few attributes that a locust class should typically define.

- task_set
should point to a TaskSet class which defines the behaviour of the user

- min_wait, max_wait:
time respectively, in milliseconds, that a simulated user will wait
between executing each task.
both default to 1000, and therefore a locust will always
wait 1 second between each task if min_wait and max_wait are not declared.

weight:
Say for example, web users are three times more likely than mobile users:
class WebUserLocust(Locust):
    weight = 3
    ....
class MobileUserLocust(Locust):
    weight = 1
    ....

host:
a URL prefix (i.e. “http://google.com”) to the host that is to be loaded.
Usually, this is specified on the command line, using the --host option,
when locust is started.
If one declares a host attribute in the locust class, it will be used
in the case when no --host is specified on the command line.



TaskSet class
-------------
If the Locust class represents a swarming locust, you could say that
the TaskSet class represents the brain of the locust.
Each Locust class must have a task_set attribute set, that points to a TaskSet.
A TaskSet is, like its name suggests, a collection of tasks.
These tasks are normal python callables and
—if we were load-testing an auction website—
could do stuff like “loading the start page”, “searching for some product” and “making a bid”.

When a load test is started, each instance of the spawned
Locust classes will start executing their TaskSet.
What happens then is that each TaskSet will pick one of its tasks and call it.
It will then wait a number of milliseconds, chosen at random between the
Locust class’ min_wait and max_wait attributes (unless min_wait/max_wait
have been defined directly under the TaskSet, in which case
it will use its own values instead).
Then it will again pick a new task to be called, wait


Declaring tasks
---------------
The typical way of declaring tasks for a TaskSet it to use the task decorator.
Here is an example:

from locust import Locust, TaskSet, task

class MyTaskSet(TaskSet):
    @task
    def my_task(self):
        print("Locust instance (%r) executing my_task" % (self.locust))

class MyLocust(Locust):
    task_set = MyTaskSet


@task takes an optional weight argument that can be used to specify the task’s execution ratio. In the following example task2 will be executed twice as much as task1:
from locust import Locust, TaskSet, task
class MyTaskSet(TaskSet):
    min_wait = 5000
    max_wait = 15000

    @task(3)
    def task1(self):
        pass

    @task(6)
    def task2(self):
        pass

tasks attribute
---------------
Using the @task decorator to declare tasks is a convenience, ....
it’s also possible to define the tasks of a TaskSet by
setting the tasks attribute (using the @task decorator will
actually just populate the tasks attribute).

The tasks attribute is either
a list of python callables, or a
<callable : int> dict.
The tasks are python callables that receive one argument
—the TaskSet class instance that is executing the task.

extremely simple example of a locustfile (won’t actually
load test anything)
EV I assume argument l is the test class instance:

from locust import Locust, TaskSet

def my_task(l):
    pass

class MyTaskSet(TaskSet):
    tasks = [my_task]

class MyLocust(Locust):
    task_set = MyTaskSet

If the tasks attribute is specified as a list, each time a task is
to be performed, it will be randomly chosen from the tasks attribute.
If however, tasks is a dict—with callables as keys and ints as values
—the task that is to be executed will be chosen at random but with
the int as ratio. So with a tasks that looks like this:

{my_task: 3, another_task:1}
my_task would be 3 times more likely to be executed than another_task.

A very important property of TaskSets is that they can be nested,
because real websites are usually built up in an hierarchical way,
with multiple sub-sections.
Nesting TaskSets will therefore allow us to define a behaviour that
simulates users in a more realistic way.

The way you nest TaskSets is just like when you specify a task using
the tasks attribute, but instead of referring to a python function,
you refer to another TaskSet:

class ForumPage(TaskSet):
    @task(20)
    def read_thread(self):
        pass

    @task(1)
    def new_thread(self):
        pass

    @task(5)
    def stop(self):
        self.interrupt()

class UserBehaviour(TaskSet):
    tasks = {ForumPage:10}

    @task
    def index(self):
        pass


above ... if the ForumPage would get selected for execution
when the UserBehaviour TaskSet is executing, then the ForumPage
TaskSet would start executing. The ForumPage TaskSet would then
pick one of its own tasks, execute it, wait, and so on.

important ... the call to self.interrupt() in the ForumPage’s stop method.
... to stop executing the ForumPage task set and the execution will
continue in the UserBehaviour instance.
If we didn’t have a call to the interrupt() method somewhere in ForumPage,
the Locust would never stop running the ForumPage task once it has started.
But by having the interrupt function, we can —together with task weighting
 —define how likely it is that a simulated user leaves the forum.


It’s also possible to declare a nested TaskSet, inline in a class,
using the @task decorator, just like when declaring normal tasks:
class MyTaskSet(TaskSet):
    @task
    class SubTaskSet(TaskSet):
        @task
        def my_task(self):
            pass
??? would it be like previoius example.
need self.interrupt() to avoid that child task executes forever?


Referencing the Locust instance, or the parent TaskSet instance
---------------------------------------------------------------
A TaskSet instance will have the attribute
- locust:  point to its Locust instance, and the attribute
parent: point to its parent TaskSet (it will point to the Locust
instance, in the base TaskSet).


Setups, Teardowns, on_start, and on_stop
----------------------------------------
Locust optionally supports
- Locust level: setup and teardown,
EVNote: generate audienceID?
- TaskSet level: setup and teardown, and
- TaskSet on_start and on_stop


order which they are run:

Locust setup
    TaskSet setup
        TaskSet on_start
            TaskSet tasks…
        TaskSet on_stop
    TaskSet teardown
Locust teardown


Making HTTP requests
--------------------
When using HttpLocust class, each instance gets a client attribute
which will be an instance of HttpSession ... to make HTTP requests.
... The client support cookies, and therefore keeps the session
between HTTP requests.

we can reference the HttpSession instance using self.client inside
the TaskSet, and not self.locust.client. We can do this because the
TaskSet class has a convenience property called client that simply
returns self.locust.client.


Using the HTTP client
---------------------
Each instance of HttpLocust has an instance of HttpSession in the
client attribute.
HttpSession class is actually a subclass of *requests.Session* and
can be used to make HTTP requests, that will be reported to Locust’s statistics,
using the get, post, put, delete, head, patch and options methods.

Here’s a simple example that makes a GET request to the /about path
(in this case we assume self is an instance of a TaskSet or HttpLocust
class:

response = self.client.get("/about")
print("Response status code:", response.status_code)
print("Response content:", response.content)
And here’s an example making a POST request:
response = self.client.post("/login", {"username":"testuser", "password":"secret"})


Safe mode
---------
The HTTP client is configured to run in safe_mode.
What this does is that any request that fails due to
a connection error, timeout, or similar will not raise
an exception, but rather return an empty dummy Response object.
The request will be reported as a failure in Locust’s statistics.
The returned dummy Response’s content attribute will be set to None,
and its status_code will be 0.


Manually ... successful or a failure
-------------------------------------------------------------------------------
By default, requests are marked as failed requests unless the HTTP
response code is OK (2xx).
Most of the time, this default is what you want.
Sometimes however—for example when testing a URL endpoint that you
expect to return 404, or testing a badly designed system that might
return 200 OK even though an error occurred—there’s a need for manually
controlling if locust should consider a request as a success or a failure.

mark requests as failed, even when the response code is OK,
by using the catch_response argument and a with statement:
# EV seems just a simple sample
with client.get("/", catch_response=True) as response:
    if response.content != "Success":
        response.failure("Got wrong response")


use catch_response argument together with a with statement to make
requests that resulted in an HTTP error code still be reported as
a success in the statistics:
with client.get("/does_not_exist/", catch_response=True) as response:
    if response.status_code == 404:
        response.success()


Grouping requests to URLs with dynamic parameters
-------------------------------------------------
It’s very common for websites to have pages whose URLs
contain some kind of dynamic parameter(s).
Often it makes sense to group these URLs together in Locust’s statistics.
This can be done by passing a name argument to the
HttpSession's different request methods.

Example:

# Statistics for these requests will be grouped under: /blog/?id=[id]
for i in range(10):
    client.get("/blog?id=%i" % i, name="/blog?id=[id]")


Common libraries
----------------
... group multiple locustfiles that share common libraries.
In that case, it is important to define the project root to
be the directory where you invoke locust, and it is
suggested that all locustfiles live somewhere beneath the project root.

A flat file structure works out of the box:

project root
- commonlib_config.py
- commonlib_auth.py
- locustfile_web_app.py
- locustfile_api.py
- locustfile_ecommerce.py
The locustfiles may import common libraries using, e.g. import commonlib_auth.
This approach does not cleanly separate common libraries from locust files,
however.


Subdirectories can be a cleaner approach (see example below), but
LOCUST WILL ONLY IMPORT MODULES RELATIVE TO THE DIRECTORY
IN WHICH THE RUNNING LOCUSTFILE IS PLACED.

If you wish to import from your PROJECT ROOT
(i.e. the location where you are running the locust command),
make sure to write sys.path.append(os.getcwd()) in your locust file(s)
before importing any common libraries—this will make the project root
(i.e. the current working directory) importable.

project root
    __init__.py
    common/
        __init__.py
        config.py
        auth.py
    locustfiles/
        __init__.py
        web_app.py
        api.py
        ecommerce.py
With the above project structure, your locust files can import
common libraries using:
sys.path.append(os.getcwd())
import common.auth

'''


from locust import HttpLocust, TaskSet

# --- da altro file
from argparse import Namespace
from locust import runners
# import locustfile



def login(l):
    l.client.post("/login", {"username":"ellen_key", "password":"education"})

def logout(l):
    l.client.post("/logout", {"username":"ellen_key", "password":"education"})

def index(l):
    l.client.get("/")

def profile(l):
    l.client.get("/profile")

class UserBehavior(TaskSet):
    tasks = {index: 2, profile: 1}

    def on_start(self):
        login(self)

    def on_stop(self):
        logout(self)

class WebsiteUser(HttpLocust):
    task_set = UserBehavior
    min_wait = 5000
    max_wait = 9000




options = Namespace()
options.host = "http://localhost"
options.num_clients = 10
options.hatch_rate = options.num_clients
options.num_requests = options.num_clients * 10

runners.locust_runner = runners.LocalLocustRunner([locustfile.MyUser], options)
runners.locust_runner.start_hatching(wait=True)
runners.locust_runner.greenlet.join()

for name, value in runners.locust_runner.stats.entries.items():
    print(name,
          value.min_response_time,
          value.median_response_time,
          value.max_response_time,
          value.total_rps)