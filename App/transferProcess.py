import os
import logging
from Events.eventTransferDataOrganizations import Adapter

current_dir = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(current_dir)
ABS_PATH = os.path.join(BASE_DIR, "App", "{}")

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
                    force=True)
logger = logging.getLogger(__name__)

# Delete the 'finish.txt' file if it exists
finish_path = ABS_PATH.format('finish.txt')
if os.path.exists(finish_path):
    os.remove(finish_path)

# Delete the 'error.txt' file if it exists
error_path = ABS_PATH.format('error.txt')
if os.path.exists(error_path):
    os.remove(error_path)

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

try:
    # Process the data and get the results
    dic_accounts = adapter.process_data()

    # Write 'finish' to the 'finish.txt' file
    with open(finish_path, 'w') as f:
        f.write('finish')

except Exception as e:
    logger.error(f"Error writing to file: {e}")
    with open(error_path, 'w') as f:
        f.write(str(e))
