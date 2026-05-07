import os
import pandas as pd
from Datacleaner import DataCleaner

class DataLoader:
    def __init__(self, folder_path):
        if not os.path.isdir(folder_path):
            raise ValueError("O caminho fornecido não é uma pasta válida.")
        
        self.folder_path = folder_path
        self.Brasileirao = None  # ← atualizado

        # Carregar os arquivos automaticamente ao inicializar
        self.load_files()

        # Relacionar as tabelas após carregamento dos dados
        # self.merge_data()
    
   
    def load_files(self):
        file_mapping = {
            'mundo_transfermarkt_competicoes_brasileirao_serie_a.csv': 'Brasileirao'
        }

        for file_name, attr in file_mapping.items():
            file_path = os.path.join(self.folder_path, file_name)
            if os.path.exists(file_path):
                df_raw = pd.read_csv(file_path)
                df_clean = DataCleaner(df_raw).clean()  # ← limpa aqui
                setattr(self, attr, df_clean)
                print(f"{file_name} carregado com sucesso.")
            else:
                print(f"Aviso: {file_name} não encontrado na pasta especificada.")