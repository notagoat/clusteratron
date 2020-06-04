#run this before to connect microk8s kubectl proxy --port=8080 &
import requests, json

host = 'localhost'
port = "8080"

namespacenames = []
deploymentimages = []
deploymentnames = []

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
i = 0
while i != len(deploymentimages):
	print("Name: %s \t Image: %s"%(deploymentnames[i],deploymentimages[i]))
	i += 1