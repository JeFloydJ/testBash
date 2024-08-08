from abc import ABC, abstractmethod
import os
from simple_salesforce import Salesforce
from typing import Dict, List

current_dir = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(current_dir)
ABS_PATH = os.path.join(BASE_DIR, "{}")

class DataStrategy(ABC):
    """
    Abstract base class for data strategies. Defines the interface that all data strategies must implement.
    """
    @abstractmethod
    def send_data(self, data: List[Dict[str, any]], object_name: str, principal_object: str, object : str, external_id: str) -> None:
        """
        Send data to Salesforce.

        Args:
            data (List[Dict[str, any]]): The data to be sent to Salesforce.
            object_name (str): The name of the Salesforce object to which data will be sent.
            principal_object (str): The name of the principal object (contact/organization/households) for report.
            object(str): name of the object to be sent to salesforce (ex: address of organization)
            external_id (str): The external ID field to be used for upserting the data.

        Returns:
            None
        """
        pass

class SalesforceStrategy(DataStrategy):
    """
    A data strategy implementation for sending data to Salesforce using the Bulk API.
    """
    def __init__(self) -> None:
        """
        Initialize the SalesforceStrategy instance. Reads the Salesforce token and initializes the Salesforce connection.
        """
        self.token: str = self._read_token()
        self.access_token: str = self._read_access_token()
        self.sf: Salesforce = self._initialize_salesforce()

    def _read_token(self) -> str:
        """
        Read the Salesforce instance token from a file.

        Returns:
            str: The Salesforce instance token.
        """
        with open(ABS_PATH.format('salesforce_instance.txt'), 'r') as f:
            instance: str = f.read().strip()

        if 'https://' in instance:
            instance = instance.split('https://')[1]

        return instance

    def _read_access_token(self) -> str:
        """
        Read the Salesforce access token from a file.

        Returns:
            str: The Salesforce access token.

        """
        with open(ABS_PATH.format('salesforce_token.txt'), 'r') as f:
            return f.read().strip()

    def _initialize_salesforce(self) -> Salesforce:
        """
        Initialize the Salesforce connection using the instance token and access token.

        Returns:
            Salesforce: An instance of the Salesforce class from the simple_salesforce library.

        """
        return Salesforce(instance=self.token, session_id=self.access_token)

    def send_data(self, data:list[dict[str, any]], object_name: str, principal_object: str, object: str ,external_id: str) -> None:
        """
        Send data to a specified Salesforce object using the bulk API.

        Args:
            data (List[Dict[str, any]]): The data to be sent to Salesforce.
            object_name (str): The name of the Salesforce object to which data will be sent.
            principal_object (str): The name of the principal object (contact/organization/households) for report.
            object(str): name of the object to be sent to salesforce (ex: address of organization)
            external_id (str): The external ID field to be used for upserting the data.
        Returns:
            None
        """
    
        results  = self.sf.bulk.__getattr__(object_name).upsert(
            data,
            external_id,
            batch_size='auto',
            use_serial=True
        )
        with open(ABS_PATH.format(f'logs/{principal_object}_{object}_response.txt'), 'w') as f:
            f.write(str(results))
        


# data =  [{
#         'RecordTypeId': '012bn0000014ppmAAA', 
#         'Auctifera__Implementation_External_ID__c': '10045', 
#         'Name': 'AT&T', 'Website': ''
#         }
#          ]

# data = [
#     {
#         'RecordTypeId': '012bn0000014ppmAAA', 
#         'Auctifera__Implementation_External_ID__c': '10045', 
#         'Name': 'AT&T', 'Website': ''
#     }
# ]

# data = [
#     {
#         'Auctifera__Implementation_External_ID__c': '123',
#         'Name': "test",
#         'Website': "test@website.com"
#     },
#     {
#         'Auctifera__Implementation_External_ID__c': '456',
#         'Name': "test2",
#         'Website': "test2@website.com"
#     }
# ]

# with open(ABS_PATH.format('salesforce_token.txt')) as f:
#     access_token = f.read().strip()

         
# with open(ABS_PATH.format('salesforce_instance.txt'), 'r') as f:
#     instance = f.read().strip()

#         #instance without "https://"
# if 'https://' in instance:
#     instance = instance.split('https://')[1]
# else:
#     instance = instance
        
# #necessary to make request in salesforce
# sf = Salesforce(instance=instance, session_id=access_token)

# res = sf.bulk.Account.upsert(data, 'Auctifera__Implementation_External_ID__c', batch_size='auto',use_serial=True)  
# print(res)

# strategy = SalesforceStrategy()
# strategy.send_data(data, 'Account', 'organization', 'Auctifera__Implementation_External_ID__c')
