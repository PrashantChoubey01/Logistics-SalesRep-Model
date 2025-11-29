

api_key= "dapibc1b1ba3a4f522480e6d9307d351c252-3"
model_name= "databricks-claude-3-7-sonnet"
base_url="https://adb-2252852771922438.18.azuredatabricks.net/serving-endpoints/"


from langchain_openai import ChatOpenAI
resp = shorten_llm.invoke("hi, ?")
print(resp.content)