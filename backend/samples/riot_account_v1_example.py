###############
### IMPORTS ###
###############

# global imports
import sys

# local imports
from __init__ import update_sys_path
update_sys_path(True)
from modules.api_clients.riot_client.services.account_v1 import ACCOUNT_V1
from models.account_dto import AccountDTO

############
### EX 1 ###
############

# # Sample Usage of Accessing AccountDTO from API given Riot ID
# response_code, json_data = ACCOUNT_V1.get_account_by_riot_id("dont ever stop", "NA1")

# print(f"Response Code: {response_code}")
# print(f"Response JSON: {json_data}")

# # store the response in AccountDTO object
# account_dto_ex_1 = AccountDTO.from_json(json_data)

# # print the AccountDTO object
# print(account_dto_ex_1)


############
### EX 2 ###
############

# Sample Usage of Accessing AccountDTO from API given Riot ID
xenux_xenux_puuid = "jcPeQ_S0lB6XTB3Sls3K43qraNgLpelztUXuqdv3ESdkGhQfYQGtzu9m6gx7TmsUlrfW02fDrN7xFw"
dont_ever_stop_na1_puuid = "g9pA1AhAi5KBJC5J_EM0cxBIbFLXEsfoJjfzz4zK0UmY-oOG69eQcvmI6U68N1xdwSq0cR2JPi7WQw"
response_code, reponse_json = ACCOUNT_V1.get_account_by_puuid(xenux_xenux_puuid)

print(f"Response Code: {response_code}")
print(f"Response JSON: {reponse_json}")

# store the response in AccountDTO object
account_dto_ex_2 = AccountDTO.from_json(reponse_json)

# print the AccountDTO object
print(account_dto_ex_2)