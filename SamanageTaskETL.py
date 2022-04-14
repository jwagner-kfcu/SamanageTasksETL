import pyodbc
import requests
import concurrent.futures
import logging
import urllib3
urllib3.disable_warnings()
import sys
sys.path.append('C:/KFCU_SSIS/Live/ServiceDeskDataLoad/python')
# 'Live/ServiceDeskDataLoad/python'
from servicedesksecret import api

# Constant values -------------------------------------------------------------------------------------------------------------
logging.basicConfig(filename='SamanageTasksETL.log', filemode='a', 
                    level=logging.DEBUG, style='{', format='{asctime} {message}')
session = requests.Session()
CallHeaders = {
                "X-Samanage-Authorization": api['key'],
                "Accept": "application/vnd.samanage.v2.1+json"
            }

counter = 0 
while True:
    PagesResponce = session.get("https://api.samanage.com/tasks.json?layout=long&updated%5B%5D=1&per_page=100", headers=CallHeaders, verify=False)
    if str(PagesResponce) == "<Response [200]>" or counter > 10:
        break
    counter = counter + 1
PageCount = PagesResponce.headers.get('X-Total-Pages', 1)
logging.debug("Total number of pages to be called - " + str(PageCount))


# Classes ---------------------------------------------------------------------------------------------------------------------
class FunctionError(Exception):
    def __init__(self, function, message):
        self.function = function
        self.message = message
        return


class Task:
    @staticmethod
    def sql():
        return """\
                   EXEC [dbo].[spMergeTask]     @id = ?, 
                                                @name = ?, 
                                                @description = ?,
                                                @requester = ?,
                                                @assigned = ?,
                                                @href = ?, 
                                                @due_at = ?,
                                                @completed_at = ?,
                                                @completed_by = ?,
                                                @created_at = ?,
                                                @task_type = ?,
                                                @state = ?,
                                                @parentid = ?,
                                                @parentname = ?,
                                                @parenttype = ?;
                   """

    def __init__(self):
        self.id = ""
        self.name = ""
        self.description = ""
        self.requester = ""
        self.assigned = ""
        self.href = ""
        self.due_at = ""
        self.completed_at = ""
        self.completed_by = ""
        self.created_at = ""
        self.task_type = ""
        self.state = ""
        self.parentid = ""
        self.parentdescription = ""
        self.parenttype = ""

    def param(self):
        return (
            self.id,
            self.name,
            self.description,
            self.requester,
            self.assigned,
            self.href,
            self.due_at,
            self.completed_at,
            self.completed_by,
            self.created_at,
            self.task_type,
            self.state,
            self.parentid,
            self.parentdescription,
            self.parenttype
        )


class db:
    def __init__(self, config):
        self.odbc_driver = ''
        self.server = config['server']
        self.db = config['db']

        try:
            if 'ODBC Driver 17 for SQL Server' in pyodbc.drivers():
                self.odbc_driver = 'ODBC Driver 17 for SQL Server'
            elif 'ODBC Driver 13.1 for SQL Server' in pyodbc.drivers():
                self.odbc_driver = 'ODBC Driver 13.1 for SQL Server'
            elif 'ODBC Driver 13 for SQL Server' in pyodbc.drivers():
                self.odbc_driver = 'ODBC Driver 13 for SQL Server'
            else:
                raise FunctionError('writetoDB', 'Missing ODBC driver')
        except FunctionError as Err:
            print('ODBC Driver Error - ({0}): {1}'.format(Err.function, Err.message))
            exit(-1)

        self.connectionstring = f'DRIVER={self.odbc_driver};SERVER={self.server};DATABASE={self.db};Trusted_Connection=yes;'
        self.conn = pyodbc.connect(self.connectionstring, autocommit=False)

    def executesql(self, ticket):
        try:
            cursor = self.conn.cursor()
            cursor.execute(ticket.sql(), ticket.param())  # params must be a tuple
            cursor.commit()
            return True
        except pyodbc.DatabaseError as Err:
            print(Err.args)
            return False

# Functions -------------------------------------------------------------------------------------------------------------------
def stripnewline(inputstring):
    if inputstring is not None:
        if inputstring != "":
            outputstring = ""
            for string in inputstring.splitlines():
                outputstring = outputstring + " " + string

            return inputstring.replace(',', ' ').replace(':', ' ').replace('/', ' ').replace('"', ' ') \
                .replace('|', ' ').lstrip().rstrip()
        return ''
    return ''


def mapTaskJSONtoObj(jsonTask):
    task = Task()
    logging.debug("mapIncidentJSONtoObj Processing - " + str(jsonTask['id']))
    for (key) in jsonTask:
        if key == 'id':
            task.id = jsonTask[key]
        elif key == 'name':
            task.name = stripnewline(jsonTask.get(key, ''))
        elif key == 'description':
            task.description = stripnewline(jsonTask.get(key, ''))
        elif key == 'requester':
            if jsonTask[key] is not None:
                for k in jsonTask[key]:
                    if k == 'name':
                        task.requester = stripnewline(jsonTask[key].get(k, ''))
            else:
                task.requester = ''
        elif key == 'assignee':
            if jsonTask[key] is not None:
                for k in jsonTask[key]:
                    if k == 'name':
                        task.assigned = stripnewline(jsonTask[key].get(k, ''))
            else:
                task.assigned = ''
        elif key == 'href':
            task.href = jsonTask.get(key, '')
        elif key == 'due_at':
            task.due_at = jsonTask.get(key, '')
        # there is no 'state' attribute returned, so this is calculated off if there is a completed date available
        elif key == 'completed_at':
            task.completed_at = jsonTask.get(key, '')
            if jsonTask[key] is not None:
                task.state = "Completed"
            else:
                task.state = "Incomplete"
        elif key == 'completed_by':
            task.completed_by = jsonTask.get(key, '')
        elif key == 'created_at':
            task.created_at = jsonTask.get(key, '')
        elif key == 'task_type':
            task.task_type = jsonTask.get(key, '')
        elif key == 'list':
            task.task_type = jsonTask.get(key, '')
        elif key == 'parent':
            if jsonTask[key] is not None:
                for k in jsonTask[key]:
                    task.parenttype = k
                    p = jsonTask[key][k]
                    for o in p:
                        if o == 'id':
                            task.parentid = jsonTask[key][k]['id']
                        elif o == 'name':
                            task.parentdescription = jsonTask[key][k]['name']
            


    connection.executesql(task)
    logging.debug("Finished Processing " + str(task.id))


def getTasks(page): 
    TaskResponce = session.get("https://api.samanage.com/tasks.json?layout=long&updated%5B%5D=1&per_page=100&page="+str(page), headers=CallHeaders, verify=False)
    logging.debug("Response for page # - " + str(TaskResponce) + "     " + str(page))
    return(TaskResponce.json())

# Body ------------------------------------------------------------------------------------------------------------------------
connection = db({
        'server': 'vspbi01',
        'db': 'Samanage'
    })

with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
    fullResponce = []
    for page in range(1, int(PageCount), 1):
        logging.debug("Request page" + str(page))
        fullResponce.append(executor.submit(getTasks, page=page))
    for future in concurrent.futures.as_completed(fullResponce):
        logging.debug("Proceses paginated response")
        for task in future.result():
            mapTaskJSONtoObj(task)
            # print(task['id'])

connection.conn.close()
exit(0)
