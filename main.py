#run this before to connect microk8s kubectl proxy --port=8080 &
import requests, json
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("host", help="The host of the kubernetes cluster")
parser.add_argument("port", help="The port of the kubernetes cluster")
parser.add_argument("--namespace", help="The namespace to search for. Use this to find deployments for a specific namespace.")

args = parser.parse_args()
print(args.host)

host = args.host
port = args.port

namespacenames = []
deploymentimages = []
deploymentnames = []
updatetimes = []
titles = ["Name", "Image", "Last Update"]

try:
	response = requests.get("http://"+host+":"+port+"/api/v1/namespaces")
except Exception as e:
	print("Could not connect to %s:%s. Make sure the host and port are correct and the proxy is enabled."%(host,port))
	exit(1)
namespaces = response.json()
#print(json.dumps(namespaces, indent=2))
namespaces = namespaces["items"]

for namespace in namespaces:
	name = namespace["metadata"]["name"]
	if args.namespace:
		if name == args.namespace:
			namespacenames.append(name)
		else:
			pass
	else:
		namespacenames.append(name)

if not namespacenames:
	print("No namespace found with the name %s. Quitting program!"%(args.namespace))
	exit(1)

#Now iterate through namespaces to get pods
for name in namespacenames:
	try:
		response = requests.get("http://"+host+":"+port+"/api/v1/namespaces/"+name+"/pods")
	except Exception as e:
		print("Could not connect to namespace pods API at http://%s:%s/api/v1/namespaces/%s/pods."%(host,port,name))
	deployments = response.json()
	deployments = deployments["items"]
	if deployments != []:
		#Found a namespace with pods!
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