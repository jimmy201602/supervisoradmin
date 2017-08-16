from django.http import HttpResponse,JsonResponse
from superadmin.utils import Config, Connection, Node, CONFIG_FILE, ProcessInfo, JsonValue
import os
import mmap
from django.views.generic import View
from django.shortcuts import render_to_response,HttpResponseRedirect,reverse,redirect
ACTIVITY_LOG = Config(CONFIG_FILE).getActivityLog()
HOST = Config(CONFIG_FILE).getHost()
from django.contrib.auth.decorators import login_required
from datetime import datetime

#activitylog
class getlogtail(View):
    def get(self,request):
        n=12
        try:
            size = os.path.getsize(ACTIVITY_LOG)
            with open(ACTIVITY_LOG, "rb") as f:
                # for Windows the mmap parameters are different
                fm = mmap.mmap(f.fileno(), 0, mmap.MAP_SHARED, mmap.PROT_READ)
            for i in xrange(size - 1, -1, -1):
                if fm[i] == '\n':
                    n -= 1
                    if n == -1:
                        break
                lines = fm[i + 1 if i else 0:].splitlines()
            return JsonResponse({'status': "success", 'log': lines})
        except Exception as err:
            return JsonResponse({'status' : "error",'messagge' : err})
        finally:
            try:
                fm.close()
            except (UnboundLocalError, TypeError):
                return JsonResponse({'status':"error", 'message': "Activity log file is empty"})



#index
class showMain(View):
# get user type
    def get(self,request):
        request.session['usertype'] = 0
        if request.session['usertype']==0:
            usertype = "Admin"
        elif request.session['usertype']==1:
            usertype = "Standart User"
        elif request.session['usertype']==2:
            usertype = "Only Log"
        elif request.session['usertype']==3:
            usertype = "Read Only"
 
        all_process_count = 0
        running_process_count = 0
        stopped_process_count = 0
        member_names = []
        environment_list = []
        g_node_list = []
        g_process_list = []
        g_environment_list = []
        group_list = []
        not_connected_node_list = []
        connected_node_list = []

        node_name_list = Config(CONFIG_FILE).node_list
        node_count = len(node_name_list)
        environment_name_list = Config(CONFIG_FILE).environment_list
        

        for nodename in node_name_list:
            nodeconfig = Config(CONFIG_FILE).getNodeConfig(nodename)

            try:
                node = Node(nodeconfig)
                if not nodename in connected_node_list:
                    connected_node_list.append(nodename);
            except Exception as err:
                if not nodename in not_connected_node_list:
                    not_connected_node_list.append(nodename);
                continue

            for name in node.process_dict2.keys():
                p_group = name.split(':')[0]
                p_name = name.split(':')[1]
                if p_group != p_name:
                    if not p_group in group_list:
                        group_list.append(p_group)

            for process in node.process_list:
                all_process_count = all_process_count + 1
                if process.state==20:
                    running_process_count = running_process_count + 1
                if process.state==0:
                    stopped_process_count = stopped_process_count + 1

        # get environment list 
        for env_name in environment_name_list:
            env_members = Config(CONFIG_FILE).getMemberNames(env_name)
            for index, node in enumerate(env_members):
                if not node in connected_node_list:
                    env_members.pop(index);
            environment_list.append(env_members)        
                    
        
        for g_name in group_list:
            tmp= []
            for nodename in connected_node_list:
                nodeconfig = Config(CONFIG_FILE).getNodeConfig(nodename)
                node = Node(nodeconfig)
                for name in node.process_dict2.keys():
                    group_name = name.split(':')[0]
                    if group_name == g_name:
                        if not nodename in tmp:
                            tmp.append(nodename)
            g_node_list.append(tmp)

        for sublist in g_node_list:
            tmp = []
            for name in sublist:
                for env_name in environment_name_list:
                    if name in Config(CONFIG_FILE).getMemberNames(env_name):
                        if name in connected_node_list:
                            if not env_name in tmp:
                                tmp.append(env_name)
            g_environment_list.append(tmp)
        
        connected_count = len(connected_node_list)
        not_connected_count = len(not_connected_node_list)

        request.session['username'] = 'jimmy'
        username = request.session['username']
        usertypecode = request.session['usertype']
        return render_to_response('index.html',locals())
                                #all_process_count =all_process_count,
                                #running_process_count =running_process_count,
                                #stopped_process_count =stopped_process_count,
                                #node_count =node_count,
                                #node_name_list = node_name_list,
                                #connected_count = connected_count,
                                #not_connected_count = not_connected_count,
                                #environment_list = environment_list,
                                #environment_name_list = environment_name_list,
                                #group_list = group_list,
                                #g_environment_list = g_environment_list,
                                #connected_node_list = connected_node_list,
                                #not_connected_node_list = not_connected_node_list,
                                #username = request.session['username'],
                                #usertype = usertype,
                                #usertypecode = request.session['usertype'])

# Show node
class showNode(View):
    def get(self,request,node_name):
        node_config = Config(CONFIG_FILE).getNodeConfig(node_name)
        add_log = open(ACTIVITY_LOG, "a")
        add_log.write("%s - %s viewed node %s .\n"%( datetime.now().ctime(), request.session['username'], node_name ))
        return JsonResponse( {'process_info' : Node(node_config).process_dict}) 

#show group
class showGroup(View):
    def get(self,request,group_name, environment_name):
        env_memberlist = Config(CONFIG_FILE).getMemberNames(environment_name)
        process_list = []
        for nodename in env_memberlist:
            node_config = Config(CONFIG_FILE).getNodeConfig(nodename)
            try:
                node = Node(node_config)
            except Exception as err:
                continue
            p_list = node.process_dict2.keys()
            for name in p_list:
                if name.split(':')[0] == group_name:
                    tmp = []
                    tmp.append(node.process_dict2[name].pid)
                    tmp.append(name.split(':')[1])
                    tmp.append(nodename)
                    tmp.append(node.process_dict2[name].uptime)
                    tmp.append(node.process_dict2[name].state)
                    tmp.append(node.process_dict2[name].statename)
                    process_list.append(tmp)
        return JsonResponse({'process_list' : process_list})


#process restart
class json_restart(View):
    def get(self,request,node_name, process_name):
        if request.session['usertype'] == 0 or request.session['usertype'] == 1:
            try:
                node_config = Config(CONFIG_FILE).getNodeConfig(node_name)
                node = Node(node_config)
                if node.connection.supervisor.stopProcess(process_name):
                    if node.connection.supervisor.startProcess(process_name):
                        add_log = open(ACTIVITY_LOG, "a")
                        add_log.write("%s - %s restarted %s node's %s process .\n"%( datetime.now().ctime(), session['username'], node_name, process_name ))
                        return JsonValue(process_name, node_name, "restart").success()
            except xmlrpclib.Fault as err:
                add_log = open(ACTIVITY_LOG, "a")
                add_log.write("%s - %s unsucces restart event %s node's %s process .\n"%( datetime.now().ctime(), session['username'], node_name, process_name ))
                return JsonValue(process_name, node_name, "restart").error(err.faultCode, err.faultString)
        else:
            add_log = open(ACTIVITY_LOG, "a")
            add_log.write("%s - %s is unauthorized user request for restart. Restart event fail for %s node's %s process .\n"%( datetime.now().ctime(), session['username'], node_name, process_name ))
            return jsonify(status = "error2",
                           message = "You are not authorized this action" )

# Process start
class json_start(View):
    def get(self,request,node_name, process_name):
        if request.session['usertype'] == 0 or request.session['usertype'] == 1:
            try:
                node_config = Config(CONFIG_FILE).getNodeConfig(node_name)
                node = Node(node_config)
                if node.connection.supervisor.startProcess(process_name):
                    add_log = open(ACTIVITY_LOG, "a")
                    add_log.write("%s - %s started %s node's %s process .\n"%( datetime.now().ctime(), session['username'], node_name, process_name ))
                    return JsonValue(process_name, node_name, "start").success()
            except xmlrpclib.Fault as err:
                add_log = open(ACTIVITY_LOG, "a")
                add_log.write("%s - %s unsucces start event %s node's %s process .\n"%( datetime.now().ctime(), session['username'], node_name, process_name ))
                return JsonValue(process_name, node_name, "start").error(err.faultCode, err.faultString)
        else:   
            add_log = open(ACTIVITY_LOG, "a")
            add_log.write("%s - %s is unauthorized user request for start. Start event fail for %s node's %s process .\n"%( datetime.now().ctime(), session['username'], node_name, process_name ))
            return JsonResponse({'status' : "error2",
                           'message' : "You are not authorized this action"} )


# Process stop
class json_stop(View):
    def get(self,request,node_name, process_name):
        if request.session['usertype'] == 0 or request.session['usertype'] == 1:
            try:
                node_config = Config(CONFIG_FILE).getNodeConfig(node_name)
                node = Node(node_config)
                if node.connection.supervisor.stopProcess(process_name):
                    add_log = open(ACTIVITY_LOG, "a")
                    add_log.write("%s - %s stopped %s node's %s process .\n"%( datetime.now().ctime(), session['username'], node_name, process_name ))
                    return JsonValue(process_name, node_name, "stop").success()
            except xmlrpclib.Fault as err:
                add_log = open(ACTIVITY_LOG, "a")
                add_log.write("%s - %s unsucces stop event %s node's %s process .\n"%( datetime.now().ctime(), session['username'], node_name, process_name ))
                return JsonValue(process_name, node_name, "stop").error(err.faultCode, err.faultString)
        else:
            add_log = open(ACTIVITY_LOG, "a")
            add_log.write("%s - %s is unauthorized user request for stop. Stop event fail for %s node's %s process .\n"%( datetime.now().ctime(), session['username'], node_name, process_name ))
            return JsonResponse({'status' : "error2",
                           'message' : "You are not authorized this action"} )

# Node name list in the configuration file
class getlist(View):
    def get(self,request):
        node_name_list = Config(CONFIG_FILE).node_list
        return JsonResponse( {'node_name_list' : node_name_list} )

# Show log for process
class readlog(View):
    def get(self,request,node_name, process_name):
        if request.session['usertype'] == 0 or request.session['usertype'] == 1 or request.session['usertype'] == 2:
            node_config = Config(CONFIG_FILE).getNodeConfig(node_name)
            node = Node(node_config)
            log = node.connection.supervisor.tailProcessStdoutLog(process_name, 0, 500)[0]
            add_log = open(ACTIVITY_LOG, "a")
            add_log.write("%s - %s read log %s node's %s process .\n"%( datetime.now().ctime(), request.session['username'], node_name, process_name ))
            return JsonResponse( {'status' : "success", 'url' : "node/"+node_name+"/process/"+process_name+"/read" , 'log' : log})
        else:
            add_log = open(ACTIVITY_LOG, "a")
            add_log.write("%s - %s is unauthorized user request for read log. Read log event fail for %s node's %s process .\n"%( datetime.now().ctime(), request.session['username'], node_name, process_name ))
            return JsonResponse( {'status' : "error", 'message' : "You are not authorized for this action"})