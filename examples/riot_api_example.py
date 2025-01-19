from __init__ import update_sys_path
update_sys_path()

from scripts.api.riot_api_client import Account_V1

# Sample Usage of Accessing AccountDTO from API given Riot ID
response_json = Account_V1.get_account_by_riot_id("dont ever stop", "NA1")
print(response_json)

# Sample Usage of Accessing AccountDTO from API given Riot ID
reponse_json = Account_V1.get_account_by_puuid("g9pA1AhAi5KBJC5J_EM0cxBIbFLXEsfoJjfzz4zK0UmY-oOG69eQcvmI6U68N1xdwSq0cR2JPi7WQw")
print(reponse_json)