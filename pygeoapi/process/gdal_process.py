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

# curl -X POST -H "Content-Type: application/json" -d "{\"inputs\":{\"name\":\"valerio\"}}" http://localhost:5000/processes/gdalinfo/execution

import logging

from pygeoapi.process.base import BaseProcessor, ProcessorExecuteError
from .manager.kubernetes_utils import *


#: Process metadata and description
PROCESS_METADATA = {
    'version': '0.0.1',
    'id': 'gdalinfo',
    'title': {
        'en': 'GdalInfo Process',
        'fr': 'Processus GdalInfo',
    },
    'description': {
        'en': 'An example process that run on kubernetes',
        'fr': 'Un exemple de processus qui execute gdalinfo sur kubernetes'
    },
    'jobControlOptions': ['sync-execute', 'async-execute'],
    'keywords': ['gdalinfo', 'example', 'echo'],
    'links': [{
        'type': 'text/html',
        'rel': 'about',
        'title': 'information',
        'href': 'https://example.org/process',
        'hreflang': 'en-US'
    }],
    'inputs':{},
    'outputs': {
        'echo': {
            'title': 'GdalInfo Process Echo',
            'description': 'A "hello world" echo with the name and (optional)'
                           ' message submitted for processing',
            'schema': {
                'type': 'object',
                'contentMediaType': 'application/json'
            }
        }
    },
    'example': {
        'inputs': {
        }
    }
}


class GdalinfoProcessor(BaseProcessor):
    """
    Gdalinfo Processor example
    """

    def __init__(self, processor_def):
        """
        Initialize object

        :param processor_def: provider definition

        :returns: pygeoapi.process.gdal_process.GdalinfoProcessor
        """

        super().__init__(processor_def, PROCESS_METADATA)

    def execute(self, data):
 
        mimetype = 'application/json'
        outputs  = k8s_execute('gdalinfo  --version')

        if outputs["status"] != "Completed":
            print(outputs["message"])
            raise ProcessorExecuteError(outputs["message"])

        return mimetype, outputs

    def __repr__(self):
        return f'<GdalinfoProcessor> {self.name}'
