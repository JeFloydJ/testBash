import logging
from Events import eventProcessData
from Events import eventDataTransfer
from patternsDesign import salesforceStrategy
import os
from dotenv import load_dotenv
from typing import Dict, List

# Set up logging
# logging.basicConfig(level=logging.INFO,
#                     format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
#                     force=True)

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
                    force=True)


logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

current_dir = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(current_dir)
ABS_PATH = os.path.join(BASE_DIR, "{}")

# hash table like: {'Auctifera__Implementation_External_ID__c': 'AccountId'} for sent address information
dic_accounts = {}
#hashtable like {'1-households-code' : 'code'}
dic_households_ids = {}
dic_households = {}

class Adapter:
    """
    Adapter class for processing data and sending it to Salesforce using different strategies.
    """
    def __init__(self, report_names: List[str]) -> None:
        """
        Initialize the Adapter instance.

        Args:
            report_names (List[str]): A list of report names to be processed.
            strategy (DataStrategy): An instance of a class implementing the DataStrategy interface.
        """
        self.report_names = report_names
        self.dic_households_ids = {}
        self.dic_accounts = {}
        self.dic_households = {}

    def process_data(self) -> None:
        global dic_accounts
        """
        Processes data using the specified strategy and sends it to Salesforce.
        """
        strategy = salesforceStrategy.SalesforceStrategy()
        for report_name in self.report_names:
            processor = eventDataTransfer.SalesforceProcessor(report_name)
            accounts, accounts_phones, address_list, phone_act_list, address_act_list = processor.process_organizations()
            if accounts:
                strategy.send_data(accounts, 'Account', 'Organizations', 'Organizations','Auctifera__Implementation_External_ID__c')  
            if accounts_phones:
                strategy.send_data(accounts_phones, 'vnfp__Legacy_Data__c', 'Organizations', 'phones' ,'vnfp__Implementation_External_ID__c')
            if address_list:
                strategy.send_data(address_list, 'npsp__Address__c', 'Organizations', 'address' ,'vnfp__Implementation_External_ID__c')
            if phone_act_list:
                strategy.send_data(phone_act_list, 'Account', 'Organizations', 'phones_update','Auctifera__Implementation_External_ID__c')
            if address_act_list:
                strategy.send_data(address_act_list, 'Account', 'Organizations', 'address_update','Auctifera__Implementation_External_ID__c') 
            _ , houseHolds_list = processor.process_households()
            self.dic_households_ids = {**self.dic_households_ids, **processor.process_households_ids()}
            processor.households_ids = self.dic_households_ids
            if houseHolds_list:
                strategy.send_data(houseHolds_list, 'Account', 'Households', 'HouseHolds','Auctifera__Implementation_External_ID__c')
            dic, contacts_list, contacts_phones_list, contacts_emails_list, contacts_act_phone, contacts_act_email= processor.process_contacts()
            self.dic_accounts = {**self.dic_accounts, **dic}
            if contacts_list:
                strategy.send_data(contacts_list, 'Contact', 'Contacts', 'Contacts','Auctifera__Implementation_External_ID__c')
            if contacts_phones_list:
                strategy.send_data(contacts_phones_list, 'vnfp__Legacy_Data__c', 'Contacts', 'phones','vnfp__Implementation_External_ID__c')
            if contacts_emails_list:
                strategy.send_data(contacts_emails_list, 'vnfp__Legacy_Data__c', 'Contacts', 'emails','vnfp__Implementation_External_ID__c')
            if contacts_act_phone:
                strategy.send_data(contacts_act_phone, 'Contact', 'Contacts', 'phone update','Auctifera__Implementation_External_ID__c')
            if contacts_act_email:  
                strategy.send_data(contacts_act_email, 'Contact', 'Contacts', 'email update','Auctifera__Implementation_External_ID__c')
            contact_adress_list = processor.process_contact_address(self.dic_accounts)
            if(contact_adress_list):
                strategy.send_data(contact_adress_list, 'npsp__Address__c', 'Contacts', 'address','vnfp__Implementation_External_ID__c')


