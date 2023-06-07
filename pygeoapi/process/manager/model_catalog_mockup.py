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
                    "command": ["gdalinfo"],
                    "args": ["--version"]
                }
            ],
            "dnsPolicy": "ClusterFirst",
            "restartPolicy": "Never"
        }
    }, # gdalinfo

    "gdal_translate" : {
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
                    "command": ["gdal_translate"],
                    "args": ["--version"]
                }
            ],
            "dnsPolicy": "ClusterFirst",
            "restartPolicy": "Never"
        }
    } # gdaltranslate

}#end model_catalog
