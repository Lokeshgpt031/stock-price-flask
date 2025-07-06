



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

    blob_service_client = BlobServiceClient.from_connection_string(StorageAccountConnectionString)

    blob_client = blob_service_client.get_blob_client(container=container_name, blob=fileName)
    try:
        with open(file=fileName, mode="rb") as data:
            blob_client.upload_blob(data)
        return fileName
    except ResourceExistsError:
        print(f"Blob '{blob_client.blob_name}' already exists.")
        return fileName
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
        formUrl =f"https://{storageAccount}.blob.core.windows.net/{container_name}/{fileName}?{sassToken}"
        document_intelligence_client  = DocumentIntelligenceClient(
            endpoint=endpoint, credential=AzureKeyCredential(key)
        )
        
        poller = document_intelligence_client.begin_analyze_document(
            "prebuilt-read", AnalyzeDocumentRequest(url_source=formUrl)
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
import groq
def summarize_with_groq(text, model=MODEL):
    client = groq.Groq()
    prompt = f"Summarize the following text:\n\n{text}"
    
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant that summarizes scanned PDF documents."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content



def fullflow(url:str):
    fileName=downloadPDFFromUrl(url)
    fileName=uploadToCloud(fileName=fileName)
    context=analyze_read(fileName=fileName)
    if(context):
        return summarize_with_groq(context)
    return "From Code: There is no text to summarize! Please provide a PDF document or text, and I'll be happy to assist you with a concise summary "

urlToDwnd="https://nsearchives.nseindia.com/corporate/BSOFT_04072025161239_SEIntimationAGMRD.pdf"


# print(fullflow(urlToDwnd))