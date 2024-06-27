# Import necessary modules
import sys
import unittest
from unittest.mock import patch, mock_open, MagicMock
sys.path.insert(1, '../')
from app import app
from app import isEmpty
from app import transferData
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(current_dir)
ABS_PATH = os.path.join(BASE_DIR, "{}")

#parameters: 
#description: test server, the server should obtain tokens in altru and salesforce
#return: result of the test
class TestApp(unittest.TestCase):

    def setUp(self):
        # Set up the test client
        self.app = app.test_client()
        app.config['TESTING'] = True

    def test_isEmpty(self):
        # test when the file is empty
        with patch("builtins.open", mock_open(read_data="")) as mock_file:
            self.assertTrue(isEmpty(mock_file.return_value))

        # test the file when is not empty
        with patch("builtins.open", mock_open(read_data="not empty")) as mock_file:
            self.assertFalse(isEmpty(mock_file.return_value))
    
    @patch('subprocess.Popen')
    def test_transferData(self, mock_popen):
        # Simula una solicitud GET a la ruta /transferData
        response = self.app.get('/transferData')

        script_path = ABS_PATH.format('transferProcess.py')  # Asegúrate de que esta ruta sea correcta
        # Verifica que la función se haya comportado como se esperaba
        self.assertEqual(response.status_code, 200)  # La respuesta debe ser 200 OK
        mock_popen.assert_called_once_with(['python3', script_path, '&'])


    @patch('builtins.open', new_callable=mock_open, read_data="not empty")
    def test_validateToken_not_empty(self, mock_file):
        # Simulate a GET request to the /Validator route when the file is not empty
        response = self.app.get('/Validator')

        # Verify that the function behaved as expected
        self.assertEqual(response.get_json(), {'status': 200})  # The response should be 200

    #parameters: 
    #description: test server, the server should obtain tokens in altru 
    #return: result of the test
    @patch('requests.post')
    def test_get_altru_token(self, mock_post):
        # Simulate a response from the Blackbaud API
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {'access_token': 'access', 'refresh_token': 'refresh'}

        # Simulate a GET request to the /skyapi/callback route with an authorization code
        response = self.app.get('/skyapi/callback?code=auth_code')

        # Verify that the function behaved as expected
        self.assertEqual(response.status_code, 404)  # The response should be a redirection

    #parameters: 
    #description: test server, the server should render the main page
    #return: result of the test
    def test_index(self):
        # Test for the index route
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)  # The response should be 200 OK

if __name__ == '__main__':
    # Run the tests
    unittest.main()
