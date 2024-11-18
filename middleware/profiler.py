import os
import requests, json
import logging
import importlib
from middleware.options import MWOptions

_logger = logging.getLogger(__name__)

def collect_profiling(options: MWOptions) -> None:
    try:
        pyroscope = importlib.import_module("pyroscope")
        if options.access_token and options.collect_profiling:

            # Setting Middleware Account Authentication URL
            auth_url = os.getenv('MW_AUTH_URL', 'https://app.middleware.io/api/v1/auth')

            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                # "Authorization": "Bearer " + c.accessToken
                "Authorization": "Bearer " + options.access_token
            }
            try:
                response = requests.post(auth_url, headers=headers)

                # Checking if auth API returns status code 200
                if response.status_code == 200:
                    data = json.loads(response.text)

                    # Checking if a tenantID could be fetched from API Key
                    if data["success"]:
                        account = data["data"]["project_uid"]
                        
                        # Setting Middleware Profiling Server URL
                        default_profiling_server_url = f'https://{account}.middleware.io/profiling'
                        profiling_server_url = os.getenv('MW_PROFILING_SERVER_URL', default_profiling_server_url)
                        
                        pyroscope.configure(
                            application_name=options.service_name,  # replace this with some name for your application
                            server_address=profiling_server_url,
                            # replace this with the address of your pyroscope server
                            tenant_id=account,
                        )
                    else:
                        _logger.warning("profiling: request failed " + data["error"])
                else:
                    _logger.warning("profiling: request failed with status code: " + str(response.status_code))
            except Exception as e:
                _logger.warning("profiling: Error making profiling request:", e)
        else:
            _logger.warning("profiling: disabled or access token not found")

    except:
        _logger.warning("profiling dependencies not found, install using `pip install middleware-io[profiling]`")