import os
from Events.eventTransferDataOrganizations import Adapter

current_dir = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(current_dir)
ABS_PATH = os.path.join(BASE_DIR, "App", "{}")

# Delete the 'finish.txt' file if it exists
if os.path.exists('finish.txt'):
    os.remove('finish.txt')

# List of report names with necessary data
report_names = [
    "Veevart Organizations Report test",
    "Veevart Organization Addresses Report test",
    "Veevart Organization Phones Report test",
    "Veevart HouseHolds Report test",
    "Veevart Contacts Report test",
    "Veevart Contacts Report Address test",
    "Veevart Contacts Report Email test",
    "Veevart Contacts Report Phones test",
    "Veevart Contacts Relationships report test",
    "Veevart Organizations Relationships report test"
]

# Create an instance of the Adapter class
adapter = Adapter(report_names)

# Process the data and get the results
dic_accounts = adapter.process_data()

# Write 'finish' to the 'finish.txt' file
finish_path = os.path.join(ABS_PATH.format(''), 'finish.txt')
with open(finish_path, 'w') as f:
    f.write('finish')
