from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
import os,uuid


# https://docs.microsoft.com/en-us/azure/storage/blobs/storage-quickstart-blobs-python

# BlobServiceClient: The BlobServiceClient class allows you to manipulate Azure Storage resources and blob containers.
# ContainerClient: The ContainerClient class allows you to manipulate Azure Storage containers and their blobs.
# BlobClient: The BlobClient class allows you to manipulate Azure Storage blobs.

# connection credentials
connect_str = os.environ['AZURE_STORAGE_CONNECTION_STRING']

#def connect():
#    connect_str = os.environ['AZURE_STORAGE_CONNECTION_STRING']
#    blob_service_client=BlobServiceClient.from_connection_string(connect_str)
#    Container_Client = blob_service_client.get_container_client("homebrewerscontainer")
#    New_Container = blob_service_client.create_container("homebrewnewcontainer")
#    props=New_Container.get_container_properties()
#    return str(props)


# create a new container

def azure_new_container(name):

    outcome_message = []
    outcome = False    
    try:
        blob_service_client=BlobServiceClient.from_connection_string(connect_str)
    except:
        outcome_message.append("could not connect")
        return outcome, outcome_message
    else:
        try:
            blob_service_client.create_container(name)
        except:
            outcome_message.append("could not create container")
            return outcome, outcome_message
        else:
            outcome_message.append("{} container created".format(name))
            outcome = True
            return outcome, outcome_message
    finally:
        outcome_message.clear

# delete a container

def azure_delete_container(name):

    outcome_message = []
    outcome = False   
    try:
        blob_service_client=BlobServiceClient.from_connection_string(connect_str)
    except:
        outcome_message.append("could not connect")
        return outcome, outcome_message
    else:
        try:
            blob_service_client.delete_container(name)
        except:
            outcome_message.append("could not delete container")
            return outcome, outcome_message
        else:
            outcome_message.append("{} container deleted".format(name))
            outcome = True
            return outcome, outcome_message
    finally:
        outcome_message.clear

# upload a blob

def azure_upload_blob(container, filepath, filename):

    outcome_message = []  
    outcome = False  
    try:
        # create the BlobServiceClient class that allows you to manipulate Azure Storage resources and blob containers.
        blob_service_client=BlobServiceClient.from_connection_string(connect_str)
        # Create a blob client using the local file name as the name for the blob
        blob_client = blob_service_client.get_blob_client(container=container, blob=filename)
    except:
        outcome_message.append("could not create blob_client")
        return outcome, outcome_message
    else:
        try:
            with open(os.path.join(filepath,filename), "rb") as data:
                blob_client.upload_blob(data)
        except:
            outcome_message.append("could not upload blob")
            return outcome, outcome_message
        else:
            outcome_message.append("{} uploaded".format(filename))
            outcome = True
            return outcome, outcome_message
    finally:
        outcome_message.clear

def azure_upload_file_object(container, content, filename):

    outcome_message = []  
    outcome = False  
    try:
        # create the BlobServiceClient class that allows you to manipulate Azure Storage resources and blob containers.
        blob_service_client=BlobServiceClient.from_connection_string(connect_str)
        # Create a blob client using the local file name as the name for the blob
        blob_client = blob_service_client.get_blob_client(container=container, blob=filename)
    except:
        outcome_message.append("could not create blob_client")
        return outcome, outcome_message
    else:
        try:
            
            blob_client.upload_blob(content)
        except:
            outcome_message.append("could not upload blob")
            return outcome, outcome_message
        else:
            outcome_message.append("uploaded")
            outcome = True
            return outcome, outcome_message
    finally:
        outcome_message.clear
