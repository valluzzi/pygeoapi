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

from datetime import datetime
import json
import logging
from pathlib import Path
from typing import Any, Dict, Tuple, Optional
import uuid
from kubernetes import client,config,utils

from pygeoapi.util import DATETIME_FORMAT,JobStatus 
from pygeoapi.process.manager.tinydb_ import TinyDBManager
from pygeoapi.process.base import BaseProcessor

LOGGER = logging.getLogger(__name__)


class KubernetesManager(TinyDBManager):
    """
    KubernetesManager
    """

    def __init__(self, manager_def: dict):
        """
        Initialize object

        :param manager_def: manager definition

        :returns: `pygeoapi.process.manager.base.BaseManager`
        """

        super().__init__(manager_def)
        config.load_kube_config()
    

    def _execute_handler_sync(self, p: BaseProcessor, job_id: str,
                              data_dict: dict) -> Tuple[str, Any, JobStatus]:
        """
        Synchronous execution handler

        If the manager has defined `output_dir`, then the result
        will be written to disk
        output store. There is no clean-up of old process outputs.

        :param p: `pygeoapi.process` object
        :param job_id: job identifier
        :param data_dict: `dict` of data parameters

        :returns: tuple of MIME type, response payload and status
        """

        process_id = p.metadata['id']
        current_status = JobStatus.accepted

        job_metadata = {
            'identifier': job_id,
            'process_id': process_id,
            'job_start_datetime': datetime.utcnow().strftime(
                DATETIME_FORMAT),
            'job_end_datetime': None,
            'status': current_status.value,
            'location': None,
            'mimetype': None,
            'message': 'Job accepted and ready for execution',
            'progress': 5
        }

        self.add_job(job_metadata)

        try:
            if self.output_dir is not None:
                filename = f"{p.metadata['id']}-{job_id}"
                job_filename = self.output_dir / filename
            else:
                job_filename = None

            current_status = JobStatus.running

            # TODO: run the pod instead  
            #outputs = k8s_execute(f"{command} --version")


            jfmt, outputs = p.execute(data_dict)
            print(jfmt, outputs)
            print("========================================")

            # 1) create a pod
            # 2) wait for the pod Running
            # 3) get the pod logs and parse the output to eventually update the job status
            # 4) delete the pod

            # --- end of process execution ---

            self.update_job(job_id, {
                'status': current_status.value,
                'message': 'Writing job output',
                'progress': 95
            })

            if self.output_dir is not None:
                LOGGER.debug(f'writing output to {job_filename}')
                if isinstance(outputs, dict):
                    mode = 'w'
                    data = json.dumps(outputs, sort_keys=True, indent=4)
                    encoding = 'utf-8'
                elif isinstance(outputs, bytes):
                    mode = 'wb'
                    data = outputs
                    encoding = None
                with job_filename.open(mode=mode, encoding=encoding) as fh:
                    fh.write(data)

            current_status = JobStatus.successful

            job_update_metadata = {
                'job_end_datetime': datetime.utcnow().strftime(
                    DATETIME_FORMAT),
                'status': current_status.value,
                'location': str(job_filename),
                'mimetype': jfmt,
                'message': 'Job complete',
                'progress': 100
            }

            self.update_job(job_id, job_update_metadata)

        except Exception as err:
            # TODO assess correct exception type and description to help users
            # NOTE, the /results endpoint should return the error HTTP status
            # for jobs that failed, ths specification says that failing jobs
            # must still be able to be retrieved with their error message
            # intact, and the correct HTTP error status at the /results
            # endpoint, even if the /result endpoint correctly returns the
            # failure information (i.e. what one might assume is a 200
            # response).

            current_status = JobStatus.failed
            code = 'InvalidParameterValue'
            outputs = {
                'code': code,
                'description': 'Error updating job'
            }
            LOGGER.error(err)
            job_metadata = {
                'job_end_datetime': datetime.utcnow().strftime(
                    DATETIME_FORMAT),
                'status': current_status.value,
                'location': None,
                'mimetype': None,
                'message': f'{code}: {outputs["description"]}'
            }

            jfmt = 'application/json'

            self.update_job(job_id, job_metadata)

        return jfmt, outputs, current_status

    