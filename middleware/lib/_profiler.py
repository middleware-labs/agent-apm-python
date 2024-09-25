import os
import requests, json
import pyroscope
from middleware.config import config

green_color = "\033[92m"
yellow_color = "\033[93m"
reset_color = "\033[0m"

def collect_profiling() -> None:
    if config.access_token != "":

        # Setting Middleware Account Authentication URL
        auth_url = os.getenv('MW_AUTH_URL', 'https://app.middleware.io/api/v1/auth')

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            # "Authorization": "Bearer " + c.accessToken
            "Authorization": "Bearer " + config.access_token
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
                        application_name=config.service_name,  # replace this with some name for your application
                        server_address=profiling_server_url,
                        # replace this with the address of your pyroscope server
                        tenant_id=account,
                    )
                else:
                    print("Request failed: " + data["error"])
            else:
                print(f"[{yellow_color}WARN{reset_color}] Profiling Request failed with status code: " + str(response.status_code))
        except Exception as e:
            print(f"[{yellow_color}WARN{reset_color}] Error making profiling request:", e)
    else:
        print(f"[{yellow_color}WARN{reset_color}] Profiling is not enabled or access token is empty")
