from abc import ABC, abstractmethod
import os
from simple_salesforce import Salesforce

current_dir = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(current_dir)
ABS_PATH = os.path.join(BASE_DIR, "{}")

class DataStrategy(ABC):
    """
    Abstract base class for data strategies. Defines the interface that all data strategies must implement.
    """
    @abstractmethod
    def send_data(self, data, object_name, principal_object, external_id):
        """
        Send data to Salesforce.

        Args:
            data (dict): The data to be sent to Salesforce.
            object_name (str): The name of the Salesforce object to which data will be sent.
            principal_object (str): The name of the principal object (contact/organization/households) for report.
            external_id (str): The external ID field to be used for upserting the data.

        Returns:
            None
        """
        pass

class SalesforceStrategy(DataStrategy):
    """
    A data strategy implementation for sending data to Salesforce using the Bulk API.
    """
    def __init__(self):
        """
        Initialize the SalesforceStrategy instance. Reads the Salesforce token and initializes the Salesforce connection.
        """
        self.token = self._read_token()
        self.access_token = self._read_access_token()
        self.sf = self._initialize_salesforce()

    def _read_token(self):
        """
        Read the Salesforce instance token from a file.

        Returns:
            str: The Salesforce instance token.
        """
        with open(ABS_PATH.format('salesforce_instance.txt'), 'r') as f:
            instance = f.read().strip()

        if 'https://' in instance:
            instance = instance.split('https://')[1]

        return instance

    def _read_access_token(self):
        """
        Read the Salesforce access token from a file.

        Returns:
            str: The Salesforce access token.
        """
        with open(ABS_PATH.format('salesforce_token.txt'), 'r') as f:
            return f.read().strip()

    def _initialize_salesforce(self):
        """
        Initialize the Salesforce connection using the instance token and access token.

        Returns:
            Salesforce: An instance of the Salesforce class from the simple_salesforce library.
        """
        return Salesforce(instance=self.token, session_id=self.access_token)

    def send_data(self, data, object_name, principal_object, external_id):
        """
        Send data to a specified Salesforce object using the bulk API.

        Args:
            data (dict): The data to be sent to Salesforce.
            object_name (str): The name of the Salesforce object to which data will be sent.
            principal_object (str): The name of the principal object (contact/organization/households) for report.
            external_id (str): The external ID field to be used for upserting the data.

        Returns:
            None
        """
        results = self.sf.bulk.__getattr__(object_name).upsert(
            data,
            external_id,
            batch_size='auto',
            use_serial=True
        )
        with open(ABS_PATH.format(f'logs/{principal_object}_{object_name}_response.txt'), 'w') as f:
            f.write(str(results))

# Example usage:
data = [
    {
        'Auctifera__Implementation_External_ID__c': '123',
        'Name': "test",
        'Website': "test@website.com"
    },
    {
        'Auctifera__Implementation_External_ID__c': '456',
        'Name': "test2",
        'Website': "test2@website.com"
    }
]

strategy = SalesforceStrategy()
strategy.send_data(data, 'Account', 'organization', 'Auctifera__Implementation_External_ID__c')
