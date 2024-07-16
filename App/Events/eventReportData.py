import csv
import os
import json

class ReportProcessor:
    def __init__(self, txt_path, json_path, csv_path):
        self.txt_path = txt_path
        self.json_path = json_path
        self.csv_path = csv_path

    def convert_to_json(self):
        with open(self.txt_path, 'r') as file, open(self.json_path, 'w') as file_json:
            for line in file:
                new_line = line.replace("'", '"').replace("True", 'true').replace("False", 'false').replace("None", 'null')
                file_json.write(new_line)
        print(f"Archivo JSON generado en {self.json_path}.")

    def generate_report_send_data(self, report_name):
        json_path = os.path.join(os.path.dirname(self.json_path), f"{report_name}.json")
        with open(json_path) as json_file:
            data = json.load(json_file)
            
            # Inicializar contadores y listas
            success_true = 0
            success_false = 0
            created_true = 0
            created_false = 0
            success_ids_true = []
            success_ids_false = []
            created_ids_true = []
            created_ids_false = []
            errors_list = []

            # Analizar los datos
            for item in data:
                if item['success']:
                    success_true += 1
                    success_ids_true.append(item['id'])
                else:
                    success_false += 1
                    success_ids_false.append(item['id'])
                
                if item['created']:
                    created_true += 1
                    created_ids_true.append(item['id'])
                else:
                    created_false += 1
                    created_ids_false.append(item['id'])
                
                if item['errors']:
                    for error in item['errors']:
                        errors_list.append({'id': item['id'], 'error': error})

            # Crear el archivo CSV basado en el nombre del reporte
            csv_file_path = os.path.join(os.path.dirname(self.csv_path), f"{report_name}.csv")
            
            with open(csv_file_path, mode='w', newline='') as file:
                writer = csv.writer(file)
                
                # Escribir encabezados
                writer.writerow(['Operation', 'True', 'False', 'Id', 'Error', 'Message Error'])
                
                # Escribir datos de Success
                writer.writerow(['Success', success_true, success_false, '', '', ''])
                for id in success_ids_true:
                    writer.writerow(['', '', '', id, '', ''])
                for id in success_ids_false:
                    writer.writerow(['', '', '', id, '', ''])
                
                # Escribir datos de Created
                writer.writerow(['Created', created_true, created_false, '', '', ''])
                for id in created_ids_true:
                    writer.writerow(['', '', '', id, '', ''])
                for id in created_ids_false:
                    writer.writerow(['', '', '', id, '', ''])
                
                # Escribir datos de errores
                writer.writerow(['Error', '', '', '', len(errors_list), ''])
                for error in errors_list:
                    writer.writerow(['', '', '', error['id'], 1, json.dumps(error['error'])])
            
            print(f"Archivo CSV generado en {csv_file_path}.")