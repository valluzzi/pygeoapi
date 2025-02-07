import re
import time
from kubernetes import client, config
import shlex
import logging
from datetime import datetime
from .model_catalog_mockup import model_catalog

LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.ERROR)


def get_command(command):
    """
    get_command
    """
    args = shlex.split(command)
    return args[0] if args else None


def parse_progress(line):
    """
    parse_progress - parse a log line in search for a progress percentage
    """
    if line:
        # match percentage in the line 
        # regexp with named group 'percentage'
        m = re.match(r".*?(?P<percent>\d+(\.\d*)?)\s*%.*?", line)
        percent = m.group("percent") if m else -1
        return float(percent)
    return -1


def manifest_from_catalog(command):
    """
    manifest_from_catalog
    """
    pod_manifest = None
    if command in model_catalog:
        pod_manifest = model_catalog[command]
        # patch the name
        name = pod_manifest["metadata"]["name"]
        pod_name = datetime.now().strftime(f"{name}-%Y%m%d%H%M%S")
        pod_manifest["metadata"]["name"] = pod_name
    return pod_manifest


def create_pod(command):
    """
    create_pod
    """
    args = shlex.split(command)
    command = args[0]
    args = args[1:]

    pod_manifest = manifest_from_catalog(command)
    if pod_manifest:
        config.load_kube_config()
        #pod_name = pod_manifest["metadata"]["name"]
        # patch the command and args
        pod_manifest["spec"]["containers"][0]["command"] = [command,]
        pod_manifest["spec"]["containers"][0]["args"] = args

        api_instance = client.CoreV1Api()

        #LOGGER.debug(f"Creating pod {pod_name}...")
        try:
            ns = "default"
            pod_name = pod_manifest["metadata"]["name"]
            # Try creating the pod
            pod = api_instance.create_namespaced_pod(
                body=pod_manifest, namespace=ns)
            LOGGER.debug(f"Pod '{pod_name}' created.")

            while pod.status.phase == "Pending":
                LOGGER.debug(f"{pod.status.phase}...")
                pod = api_instance.read_namespaced_pod(
                    name=pod_name, namespace=ns)
                time.sleep(0.5)
            
            logs = api_instance.read_namespaced_pod_log(
                name=pod_name, namespace=ns, follow=True, _preload_content=False)
            return logs.stream()
            
        except client.rest.ApiException as ex:
            LOGGER.error(f"Unknown error:{ex}")
    
    return None


def wait_for_pod(pod):
    """
    wait_for_pod - wait for the pod to be running
    """
    if pod and pod.metadata:
        try:
            api_instance = client.CoreV1Api()
            pod_name = pod.metadata.name
            namespace = pod.metadata.namespace
            # wait for the pod to be running
            while pod.status.phase == "Pending":
                #LOGGER.debug(f"{pod.status.phase}...")
                pod = api_instance.read_namespaced_pod(
                    name=pod_name, namespace=namespace)
                time.sleep(0.5)
        except client.rest.ApiException as ex:
            LOGGER.error(f"Unknown error:{ex}")


def get_stream(pod):
    """
    get_stream
    """
    wait_for_pod(pod)
    if pod and pod.metadata:
        try:
            api_instance = client.CoreV1Api()
            pod_name = pod.metadata.name
            namespace = pod.metadata.namespace
            # get the pod logs
            logs = api_instance.read_namespaced_pod_log(
                name=pod_name, namespace=namespace, follow=True, _preload_content=False)
            return logs.stream()
        except client.rest.ApiException as ex:
            LOGGER.error(f"Unknown error:{ex}")
    return None


def read_log(pod, close=False):
    """
    read_log
    """
    res = ""
    if pod and pod.metadata:
        try:
            api_instance = client.CoreV1Api()
            pod_name = pod.metadata.name
            namespace = pod.metadata.namespace
            # wait for the pod to be running
            while pod.status.phase == "Pending":
                #LOGGER.debug(f"{pod.status.phase}...")
                pod = api_instance.read_namespaced_pod(
                    name=pod_name, namespace=namespace)
                time.sleep(0.5)
            # get the pod logs
            logs = api_instance.read_namespaced_pod_log(
                name=pod_name, namespace=namespace, follow=True, _preload_content=False)
            for line in logs.stream():
                line = line.decode('utf-8')
                p = parse_progress(line)
                if p>=0:
                    # update the progress
                    pass
                res+=line 

            if close:
                api_instance.delete_namespaced_pod(
                    name=pod_name, namespace=namespace, body=client.V1DeleteOptions())
                #LOGGER.debug(f"Pod '{pod_name}' deleted.")

        except client.rest.ApiException as ex:
            LOGGER.error(f"Exception when retrieving Pod logs: {ex}")
    return res


def delete_pod(pod):
    """
    delete_pod
    """
    res = False
    if pod and pod.metadata:
        pod_name = pod.metadata.name
        namespace = pod.metadata.namespace
        api_instance = client.CoreV1Api()
        try:
            api_instance.delete_namespaced_pod(
                name=pod_name, namespace=namespace, body=client.V1DeleteOptions())
            #LOGGER.debug(f"Pod '{pod_name}' deleted.")
            res = True
        except client.rest.ApiException as ex:
            LOGGER.error(f"Exception when deleting Pod: {ex}")

    return res


def k8s_execute(command):
    """
    k8s_execute
    """
    pod = create_pod(command)
    if pod:
        outputs = read_log(pod, True)
        return {
            "id": pod.metadata.name,
            "status": "Completed",
            "message": outputs
        }
    
    command_name = get_command(command)
    return {
        "id": command_name,
        "status": "Failed",
        "message": f"Cannot find {command_name} in model catalog."
    }