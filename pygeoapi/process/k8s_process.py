# =================================================================
#
# Authors: Valerio Luzzi <valluzzi@gmail.com>
#
# Copyright (c) 2023 Valerio Luzzi
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
# =================================================================

# C:\Users\vlr20>curl -X POST -H "Content-Type: application/json"  -d "{\"mode\":\"sync\",\"inputs\":{\"command\":\"gdal_translate\"}}" http://localhost:5000/processes/k8s/execution
from pygeoapi.process.base import BaseProcessor, ProcessorExecuteError
from .manager.kubernetes_utils import *


#: Process metadata and description
PROCESS_METADATA = {
    'version': '0.0.1',
    'id': 'k8s',
    'title': {
        'en': 'Kubernetes Process',
        'fr': 'Processus Kubernetes',
    },
    'description': {
        'en': 'An generic example process that run on kubernetes',
        'fr': 'Un generic exemple de processus qui execute sur kubernetes'
    },
    'jobControlOptions': ['sync-execute', 'async-execute'],
    'keywords': ['kubernetes', 'k8s'],
    'links': [{
        'type': 'text/html',
        'rel': 'about',
        'title': 'information',
        'href': 'https://example.org/process',
        'hreflang': 'en-US'
    }],
    'inputs': {
        'command': {
            'title': 'command',
            'description': 'The commad string to execute on kubernet pod',
            'schema': {
                'type': 'string'
            },
            'minOccurs': 1,
            'maxOccurs': 1,
            'metadata': None,  # TODO how to use?
            # 'keywords': ['full name', 'personal']
        },
    },
    'outputs': {
        'echo': {
            'title': 'Generic Kubernetes Process',
            'description': 'A generic kubernetes process',
            'schema': {
                'type': 'object',
                'contentMediaType': 'application/json'
            }
        }
    },
    'example': {
        'inputs': {
            'image': 'docker.io/valerioluzzi/gdal:latest',
            'command': 'gdalinfo --version'
        }
    }
}


class K8sProcessor(BaseProcessor):
    """
    K8sProcessor Processor implementation
    """

    def __init__(self, processor_def):
        """
        Initialize object

        :param processor_def: provider definition

        :returns: pygeoapi.process.k8s_process.K8sProcessor
        """
        super().__init__(processor_def, PROCESS_METADATA)

    def check_inputs(self, data):
        """
        check inputs validity
        """
        if 'command' not in data:
            return False
        if not data['command']:
            return False

        return True

    def execute(self, data):

        if self.check_inputs(data):

            command = data['command']

            outputs = k8s_execute(f"{command} --version")

            if outputs["status"] != "Completed":
                print(outputs["message"])
                raise ProcessorExecuteError(outputs["message"])

            mimetype = 'application/json'
            return mimetype, outputs
        else:
            print("1b)")
            raise ProcessorExecuteError('Missing command parameter')

    def __repr__(self):
        return f'<K8sProcessor> {self.name}'
