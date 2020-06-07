#run this before to connect microk8s kubectl proxy --port=8080 &
import requests, json

host = 'localhost'
port = "8080"

namespacenames = []
deploymentimages = []
deploymentnames = []
updatetimes = []


print("Connecting to Kubernetes Cluster: %s:%s" %(host, port))

response = requests.get("http://"+host+":"+port+"/api/v1/namespaces")
namespaces = response.json()
#print(json.dumps(namespaces, indent=2))
namespaces = namespaces["items"]

#Get names of all running namespaces TODO: Add command line to pick only one namespace
for namespace in namespaces:
	name = namespace["metadata"]["name"]
	namespacenames.append(name)

#Now iterate through namespaces to get pods
for name in namespacenames:
	response = requests.get("http://"+host+":"+port+"/api/v1/namespaces/"+name+"/pods")
	deployments = response.json()
	deployments = deployments["items"]
	if deployments == []:
		print("No Pods Found in Namespace %s"%(name)) 
	else:
		#Found a namespace with pods!
		print("Pods Found in Namespace %s"%(name))
		for deployment in deployments:
			images = deployment["spec"]["containers"]
			for image in images:
				deploymentimages.append(image["image"])
				deploymentnames.append(image["name"])
		#Finally, Get last update. Check all historical events for each pod, then for those that have event, record time.
		for deployment in deployments:
			operation = deployment["metadata"]["managedFields"][0]["operation"]
			if operation == "Update":
				updatetimes.append(deployment["metadata"]["managedFields"][0]["time"])
			else:
				updatetimes.append("NA")


i = 0
while i != len(deploymentimages):
	print("Name: %s \t Image: %s \t Last Update Time: %s"%(deploymentnames[i],deploymentimages[i],updatetimes[i]))
	i += 1

#TODO: Improve Printing
#TODO: Make sure data stays related (EG if one deployment image detail is missing)
#TODO: Add checking for last update by checking operations then comparing dates
#TODO: Add checks for failed requests (401, bad data, exceptions with network, etc)
#TODO: Add thruple class
#TODO: kube-controller-manager vs kubelet