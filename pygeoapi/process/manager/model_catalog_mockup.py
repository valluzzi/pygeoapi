model_catalog = {

    "gdalinfo" : {
        "apiVersion": "v1",
        "kind": "Pod",
        "metadata": {
            "name": "gdal",
            "labels": {
                "run": "gdal"
            }
        },
        "spec": {
            "imagePullSecrets": [
                {
                    "name": "dockerhub-pull"
                }
            ],
            "containers": [
                {
                    "image": "docker.io/valluzzi/gdal:latest",
                    "name": "gdal",
                    "command": ["gdal"],
                    "args": ["--version"]
                }
            ],
            "dnsPolicy": "ClusterFirst",
            "restartPolicy": "Never"
        }
    }, # gdalinfo

}#end model_catalog
