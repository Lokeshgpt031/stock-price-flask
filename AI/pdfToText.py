from dotenv import load_dotenv
load_dotenv()
import os
container_name = "ai-test"
storageAccount=os.getenv("storageAccount")
endpoint = "https://360documents.cognitiveservices.azure.com/"
AIDocumentKey= os.getenv('AIDocumentKey')
MODEL= os.getenv('MODEL')
# sassToken= os.getenv('sassToken')
StorageAccountConnectionString= os.getenv('StorageAccountConnectionString')

#%%
import requests
def downloadPDFFromUrl(url:str):
    # The URL of the PDF file
    fileName=url.split("/")[-1]

    # Optional headers (application/pdf usually not required for GET, but can be added)
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/pdf"
    }

    # Send the GET request
    response = requests.get(url, headers=headers,allow_redirects=True)

    # Check if the request was successful
    if response.status_code == 200:
        # Save the PDF to a file
        with open(fileName, "wb") as f:
            f.write(response.content)
        print("PDF downloaded successfully.")
    else:
        print(f"Failed to download PDF. Status code: {response.status_code}")
    return fileName

def uploadToCloud(fileName:str):        
    from azure.storage.blob import BlobServiceClient
    from azure.core.exceptions import ResourceExistsError
    from azure.storage.blob import BlobServiceClient, BlobSasPermissions, generate_blob_sas
    from datetime import datetime, timedelta, timezone

    
    blob_service_client = BlobServiceClient.from_connection_string(StorageAccountConnectionString)

    blob_client = blob_service_client.get_blob_client(container=container_name, blob=fileName)
    # Generate SAS token
    sas_token = generate_blob_sas(
        account_name=blob_service_client.account_name,
        account_key=blob_service_client.credential.account_key,
        container_name=container_name,
        blob_name=fileName,
        permission=BlobSasPermissions(read=True, write=True),

        start = datetime.now(timezone.utc),
        expiry = datetime.now(timezone.utc) + timedelta(hours=1)
    )

    try:
        with open(file=fileName, mode="rb") as data:
            blob_client.upload_blob(data)
        return f"{blob_client.url}?{sas_token}"
    except ResourceExistsError:
        print(f"Blob '{blob_client.blob_name}' already exists.")
        return f"{blob_client.url}?{sas_token}"
    except Exception as e:
        print(f"Unexpected error occurred: {e}")
        return None

def analyze_read(fileName:str):
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.documentintelligence import DocumentIntelligenceClient
    from azure.ai.documentintelligence.models import AnalyzeDocumentRequest
    # sample document
    from azure.core.exceptions import HttpResponseError
    try:
        document_intelligence_client  = DocumentIntelligenceClient(
            endpoint=endpoint, credential=AzureKeyCredential(AIDocumentKey)
        )
        
        poller = document_intelligence_client.begin_analyze_document(
            "prebuilt-read", AnalyzeDocumentRequest(url_source=fileName)
        )
        result = poller.result()

        return result.content
    except HttpResponseError as err:
        print("Exception :",err.message)
        return None

    except Exception as e:
        print(f"Unexpected error occurred: {e}")
        return None



# %%
from agno.agent import Agent, RunResponse
from agno.models.groq import Groq
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.yfinance import YFinanceTools
# Initialize the agent with an LLM via Groq and DuckDuckGoTools
from agno.utils.pprint import pprint_run_response

from agno.agent import Agent, RunResponse
from agno.models.groq import Groq
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.utils.pprint import pprint_run_response

# Define your model ID, e.g., "mixtral-8x7b-32768"
# MODEL = "mixtral-8x7b-32768"  # You can change this to whatever model you're using

def summarize_with_groq(text, model=MODEL):
    web_agent = Agent(
        name="Web Agent",
        role="You are an enthusiastic Financial Analyst and Good Storytelling Reporter",
        model=Groq(id=model),
        tools=[DuckDuckGoTools()],  # Add other tools like YFinanceTools if needed
        show_tool_calls=True,
        instructions="Always include sources",
        markdown=True
    )
    finance_agent = Agent(
        name="Finance Agent",
        role="Get financial data",
        model=Groq(id=model),
        tools=[YFinanceTools(stock_price=True, analyst_recommendations=True, company_info=True)],
        instructions="Use tables to display data",
        markdown=True,
    )
    agent_team = Agent(
        team=[web_agent, finance_agent],
        model=Groq(id=model),  # You can use a different model for the team leader agent
        instructions=["Always include sources", "Use tables to display data"],
        # show_tool_calls=True,  # Uncomment to see tool calls in the response
        markdown=True,
    )

    # Run the agent with the provided text
    response: RunResponse = agent_team.run(text)
    # Return markdown-formatted output
    return response.content


# print(summarize_with_groq(analyze_read("BHARTIARTL_11072025151943_AGM2025_Pread.pdf")))

def fullflow(url:str):
    fileName=downloadPDFFromUrl(url)
    file_path=fileName
    fileName=uploadToCloud(fileName=fileName)
    context=analyze_read(fileName=fileName)
    if(context):
        import os
        # Check if the file exists
        if os.path.exists(file_path):
            os.remove(file_path)
            print("File deleted successfully.")
        else:
            print("File does not exist.")

        return summarize_with_groq(context)
    return "From Code: There is no text to summarize! Please provide a PDF document or text, and I'll be happy to assist you with a concise summary "

# urlToDwnd="https://nsearchives.nseindia.com/corporate/BSOFT_04072025161239_SEIntimationAGMRD.pdf"


# print(fullflow(urlToDwnd))