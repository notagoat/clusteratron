#run this before to connect microk8s kubectl proxy --port=8080 &
import requests, json

host = 'localhost'
port = "8080"

namespacenames = []
deploymentimages = []
deploymentnames = []
updatetimes = []
titles = ["Name", "Image", "Last Update"]

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


content = [titles] + list(zip(deploymentnames, deploymentimages, updatetimes))
#content is a three set tuple for printing data. It could be useful to create one of these at the start to store data but that would require moving code around a lot.

for i, c in enumerate(content):
	line = '|'.join(str(x).ljust(40) for x in c) #Might be cool to find the longest data for each section then add them?
	print(line)
	if i == 0:
		print('-' * len(line))


#TODO: Improve Printing. DONE!
#TODO: Make sure data stays related (EG if one deployment image detail is missing)
#TODO: Add checks for failed requests (401, bad data, exceptions with network, etc)
#TODO: kube-controller-manager vs kubelet