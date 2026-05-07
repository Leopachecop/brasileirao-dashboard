import pandas as pd

class DataCleaner:
    def __init__(self, df):
        self.df = df.copy()
    
    def clean(self):
        self._fix_types()
        self._fix_team_names()
        self._add_result_columns()
        return self.df
    
    def _fix_types(self):
        # Converte data para datetime
        self.df['data'] = pd.to_datetime(self.df['data'], errors='coerce')
        
        # Garante que ano é inteiro
        self.df['ano_campeonato'] = self.df['ano_campeonato'].astype(int)
        
        # Preenche o valor nulo de gol com um 0
        self.df['gols_mandante'] = self.df['gols_mandante'].fillna(0).astype(int)
        self.df['gols_visitante'] = self.df['gols_visitante'].fillna(0).astype(int)
    
    def _fix_team_names(self):
        # Unifica nomes duplicados de times
        substituicoes = {
            'Athletico-PR': 'Athletico-PR',
            'Atlético-PR':  'Athletico-PR',  # mesmo time, nome antigo
            'Goiás EC':     'Goiás',
            'Santos FC':    'Santos',
        }
        self.df['time_mandante'] = self.df['time_mandante'].replace(substituicoes)
        self.df['time_visitante'] = self.df['time_visitante'].replace(substituicoes)
    
    def _add_result_columns(self):
        # Resultado de cada jogo (útil para várias análises)
        self.df['resultado_mandante'] = self.df.apply(
            lambda r: 'vitoria' if r['gols_mandante'] > r['gols_visitante']
                      else 'derrota' if r['gols_mandante'] < r['gols_visitante']
                      else 'empate', axis=1
        )
        
        # Total de gols da partida
        self.df['total_gols'] = self.df['gols_mandante'] + self.df['gols_visitante']