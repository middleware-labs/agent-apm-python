import os
import requests, json
import pyroscope

mw_agent_target = os.environ.get('MW_AGENT_SERVICE', '127.0.0.1')


def collect_profiling(service_name, access_token="") -> None:
    if access_token != "":

        # Setting Middleware Account Authentication URL
        auth_url = os.getenv('MW_AUTH_URL', 'https://app.middleware.io/api/v1/auth')

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            # "Authorization": "Bearer " + c.accessToken
            "Authorization": "Bearer " + access_token
        }
        try:
            response = requests.post(auth_url, headers=headers)

            # Checking if auth API returns status code 200
            if response.status_code == 200:
                data = json.loads(response.text)

                # Checking if a tenantID could be fetched from API Key
                if data["success"]:
                    account = data["data"]["account"]
                    
                    # Setting Middleware Profiling Server URL
                    default_profiling_server_url = f'https://{account}.middleware.io/profiling'
                    profiling_server_url = os.getenv('MW_PROFILING_SERVER_URL', default_profiling_server_url)
                    
                    pyroscope.configure(
                        application_name=service_name,  # replace this with some name for your application
                        server_address=profiling_server_url,
                        # replace this with the address of your pyroscope server
                        tenant_id=account,
                    )
                else:
                    print("Request failed: " + data["error"])
            else:
                print("Request failed with status code: " + str(response.status_code))
        except Exception as e:
            print("Error making request:", e)
    else:
        print("Profiling is not enabled or access token is empty")
