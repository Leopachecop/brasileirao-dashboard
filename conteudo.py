import pandas as pd
import numpy as np

class Conteudo:
    def __init__(self, df):
        self.df = df
    
    # ─── VISÃO GERAL ────────────────────────────────
    def campeoes_por_ano(self):
        ultimo_jogo = self.df.groupby('ano_campeonato')['rodada'].max().reset_index()
        ultimo_jogo.columns = ['ano_campeonato', 'ultima_rodada']
        
        df_final = self.df.merge(ultimo_jogo, on='ano_campeonato')
        df_final = df_final[df_final['rodada'] == df_final['ultima_rodada']]
        
        campeao_mandante = df_final[df_final['colocacao_mandante'] == 1][['ano_campeonato', 'time_mandante']].rename(columns={'time_mandante': 'campeao'})
        campeao_visitante = df_final[df_final['colocacao_visitante'] == 1][['ano_campeonato', 'time_visitante']].rename(columns={'time_visitante': 'campeao'})
        
        campeoes = pd.concat([campeao_mandante, campeao_visitante]).drop_duplicates('ano_campeonato')
        campeoes = campeoes.sort_values('ano_campeonato', ascending=False).reset_index(drop=True)
        
        ranking = campeoes.groupby('campeao').agg(
            titulos=('ano_campeonato', 'count'),
            ultimo_titulo=('ano_campeonato', 'max'),
            anos=('ano_campeonato', lambda x: ', '.join(map(str, sorted(x))))
        ).reset_index()

        ranking = ranking.sort_values(
            ['titulos', 'ultimo_titulo'], 
            ascending=[False, False]
        ).reset_index(drop=True)
        ranking.index += 1
    
        return campeoes, ranking

    def gols_e_tendencia(self):
        gols = self.df.groupby('ano_campeonato').agg(
            total_gols=('total_gols', 'sum'),
            media_gols=('total_gols', 'mean'),
            partidas=('total_gols', 'count')
        ).reset_index()
        
        x = gols['ano_campeonato'].values
        y = gols['media_gols'].values
        coef = np.polyfit(x, y, 1)
        gols['tendencia'] = np.polyval(coef, x)
        
        return gols

    def vantagem_mandante(self):
        def calcular(g):
            return pd.Series({
                'pct_vitoria_mandante': (g['resultado_mandante'] == 'vitoria').mean() * 100,
                'pct_empate': (g['resultado_mandante'] == 'empate').mean() * 100,
                'pct_vitoria_visitante': (g['resultado_mandante'] == 'derrota').mean() * 100,
            })
        
        por_ano = self.df.groupby('ano_campeonato')[['resultado_mandante']].apply(
            calcular, include_groups=False
        ).reset_index()
        
        return por_ano

    # ─── TIMES ──────────────────────────────────────
    def aproveitamento_time(self, time):
    # Filtra jogos do time como mandante e visitante
        mandante = self.df[self.df['time_mandante'] == time].copy()
        visitante = self.df[self.df['time_visitante'] == time].copy()
        
        # Resultado do ponto de vista do time
        mandante['resultado_time'] = mandante['resultado_mandante']
        visitante['resultado_time'] = visitante['resultado_mandante'].map({
            'vitoria': 'derrota',
            'derrota': 'vitoria',
            'empate': 'empate'
        })
        
        todos = pd.concat([mandante, visitante])
        
        total = len(todos)
        vitorias = (todos['resultado_time'] == 'vitoria').sum()
        empates = (todos['resultado_time'] == 'empate').sum()
        derrotas = (todos['resultado_time'] == 'derrota').sum()
        gols_marcados = mandante['gols_mandante'].sum() + visitante['gols_visitante'].sum()
        gols_sofridos = mandante['gols_visitante'].sum() + visitante['gols_mandante'].sum()
        
        return {
            'total': total,
            'vitorias': int(vitorias),
            'empates': int(empates),
            'derrotas': int(derrotas),
            'pct_vitoria': round(vitorias / total * 100, 1),
            'pct_empate': round(empates / total * 100, 1),
            'pct_derrota': round(derrotas / total * 100, 1),
            'gols_marcados': int(gols_marcados),
            'gols_sofridos': int(gols_sofridos),
            'saldo': int(gols_marcados - gols_sofridos)
        }

    def desempenho_mandante_visitante(self, time):
        mandante = self.df[self.df['time_mandante'] == time]
        visitante = self.df[self.df['time_visitante'] == time]
        
        def calcular(df, tipo):
            if tipo == 'mandante':
                resultados = df['resultado_mandante']
            else:
                resultados = df['resultado_mandante'].map({
                    'vitoria': 'derrota',
                    'derrota': 'vitoria',
                    'empate': 'empate'
                })
            total = len(df)
            return {
                'tipo': 'Mandante' if tipo == 'mandante' else 'Visitante',
                'vitorias': round((resultados == 'vitoria').sum() / total * 100, 1),
                'empates': round((resultados == 'empate').sum() / total * 100, 1),
                'derrotas': round((resultados == 'derrota').sum() / total * 100, 1),
            }
        
        return pd.DataFrame([
            calcular(mandante, 'mandante'),
            calcular(visitante, 'visitante')
        ])

    def evolucao_time(self, time):
        mandante = self.df[self.df['time_mandante'] == time].copy()
        visitante = self.df[self.df['time_visitante'] == time].copy()
        
        mandante['resultado_time'] = mandante['resultado_mandante']
        visitante['resultado_time'] = visitante['resultado_mandante'].map({
            'vitoria': 'derrota',
            'derrota': 'vitoria',
            'empate': 'empate'
        })
        
        todos = pd.concat([mandante[['ano_campeonato', 'resultado_time']],
                        visitante[['ano_campeonato', 'resultado_time']]])
        
        evolucao = todos.groupby('ano_campeonato').apply(
            lambda g: pd.Series({
                'aproveitamento': (g['resultado_time'] == 'vitoria').mean() * 100,
                'jogos': len(g)
            }), include_groups=False
        ).reset_index()
        
        return evolucao

    def head_to_head(self, time1, time2):
        jogos = self.df[
            ((self.df['time_mandante'] == time1) & (self.df['time_visitante'] == time2)) |
            ((self.df['time_mandante'] == time2) & (self.df['time_visitante'] == time1))
        ].copy()
        
        def resultado_time1(row):
            if row['time_mandante'] == time1:
                return row['resultado_mandante']
            else:
                mapa = {'vitoria': 'derrota', 'derrota': 'vitoria', 'empate': 'empate'}
                return mapa[row['resultado_mandante']]
        
        jogos['resultado_time1'] = jogos.apply(resultado_time1, axis=1, result_type='reduce')
        
        total = len(jogos)
        return {
            'total': total,
            'vitorias_time1': int((jogos['resultado_time1'] == 'vitoria').sum()),
            'empates': int((jogos['resultado_time1'] == 'empate').sum()),
            'vitorias_time2': int((jogos['resultado_time1'] == 'derrota').sum()),
            'gols_time1': int(jogos.apply(lambda r: r['gols_mandante'] if r['time_mandante'] == time1 else r['gols_visitante'], axis=1).sum()),
            'gols_time2': int(jogos.apply(lambda r: r['gols_mandante'] if r['time_mandante'] == time2 else r['gols_visitante'], axis=1).sum()),
            'jogos': jogos[['ano_campeonato', 'data', 'time_mandante', 'time_visitante', 'gols_mandante', 'gols_visitante']].sort_values('data', ascending=False)
        }

    def ranking_times(self):
        times = pd.concat([
            self.df['time_mandante'],
            self.df['time_visitante']
        ]).unique()
        
        rows = []
        for time in sorted(times):
            ap = self.aproveitamento_time(time)
            rows.append({
                'Time': time,
                'Jogos': ap['total'],
                'Vitórias': ap['vitorias'],
                'Empates': ap['empates'],
                'Derrotas': ap['derrotas'],
                'Aproveitamento %': ap['pct_vitoria'],
                'Gols Marcados': ap['gols_marcados'],
                'Saldo de Gols': ap['saldo']
            })
        
        ranking = pd.DataFrame(rows).sort_values('Aproveitamento %', ascending=False).reset_index(drop=True)
        ranking.index += 1
        return ranking
    
    def evolucao_h2h(self, time1, time2):
        jogos = self.df[
            ((self.df['time_mandante'] == time1) & (self.df['time_visitante'] == time2)) |
            ((self.df['time_mandante'] == time2) & (self.df['time_visitante'] == time1))
        ].copy()

        def resultado_time1(row):
            if row['time_mandante'] == time1:
                return row['resultado_mandante']
            else:
                mapa = {'vitoria': 'derrota', 'derrota': 'vitoria', 'empate': 'empate'}
                return mapa[row['resultado_mandante']]

        jogos['resultado_time1'] = jogos.apply(resultado_time1, axis=1, result_type='reduce')

        evolucao = jogos.groupby('ano_campeonato').apply(
            lambda g: pd.Series({
                f'aproveitamento_{time1}': (g['resultado_time1'] == 'vitoria').mean() * 100,
                f'aproveitamento_{time2}': (g['resultado_time1'] == 'derrota').mean() * 100,
            }), include_groups=False
        ).reset_index()

        return evolucao
    
    def historico_time(self, time):
        pass
    
    # ─── PARTIDAS ───────────────────────────────────
    def recordes_historicos(self):
        # Maior goleada
        df = self.df.copy()
        df['diferenca'] = abs(df['gols_mandante'] - df['gols_visitante'])
        maior_goleada = df.loc[df['diferenca'].idxmax()]
        
        # Jogo com mais gols
        mais_gols = df.loc[df['total_gols'].idxmax()]
        
        # Maior público
        maior_publico = df.loc[df['publico'].idxmax()]
        
        return {
            'maior_goleada': {
                'placar': f"{maior_goleada['time_mandante']} {int(maior_goleada['gols_mandante'])} x {int(maior_goleada['gols_visitante'])} {maior_goleada['time_visitante']}",
                'ano': int(maior_goleada['ano_campeonato']),
                'diferenca': int(maior_goleada['diferenca'])
            },
            'mais_gols': {
                'placar': f"{mais_gols['time_mandante']} {int(mais_gols['gols_mandante'])} x {int(mais_gols['gols_visitante'])} {mais_gols['time_visitante']}",
                'ano': int(mais_gols['ano_campeonato']),
                'total': int(mais_gols['total_gols'])
            },
            'maior_publico': {
                'jogo': f"{maior_publico['time_mandante']} x {maior_publico['time_visitante']}",
                'estadio': maior_publico['estadio'],
                'publico': int(maior_publico['publico']),
                'ano': int(maior_publico['ano_campeonato'])
            },
            'total_partidas': len(df),
            'total_gols': int(df['total_gols'].sum()),
            'media_gols': round(df['total_gols'].mean(), 2)
        }

    def maiores_goleadas(self, n=10):
        df = self.df.copy()
        df['diferenca'] = abs(df['gols_mandante'] - df['gols_visitante'])
        
        goleadas = df.nlargest(n, 'diferenca')[
            ['ano_campeonato', 'data', 'time_mandante', 'gols_mandante', 
            'gols_visitante', 'time_visitante', 'diferenca', 'estadio']
        ].copy()
        
        goleadas['placar'] = goleadas.apply(
            lambda r: f"{int(r['gols_mandante'])} x {int(r['gols_visitante'])}", axis=1
        )
        
        goleadas = goleadas.rename(columns={
            'ano_campeonato': 'Ano',
            'time_mandante': 'Mandante',
            'time_visitante': 'Visitante',
            'diferenca': 'Diferença',
            'estadio': 'Estádio',
            'placar': 'Placar'
        }).drop(columns=['gols_mandante', 'gols_visitante', 'data'])
        
        return goleadas.reset_index(drop=True)

    def maiores_publicos(self, n=10):
        df = self.df.dropna(subset=['publico']).copy()
        
        maiores = df.nlargest(n, 'publico')[
            ['ano_campeonato', 'time_mandante', 'time_visitante', 
            'publico', 'publico_max', 'estadio']
        ].copy()
        
        maiores['ocupacao_%'] = (maiores['publico'] / maiores['publico_max'] * 100).round(1)
        
        maiores = maiores.rename(columns={
            'ano_campeonato': 'Ano',
            'time_mandante': 'Mandante',
            'time_visitante': 'Visitante',
            'publico': 'Público',
            'publico_max': 'Capacidade',
            'estadio': 'Estádio',
            'ocupacao_%': 'Ocupação %'
        })
        
        return maiores.reset_index(drop=True)

    def gols_por_rodada(self):
        rodada = self.df.groupby('rodada').agg(
            media_gols=('total_gols', 'mean'),
            total_gols=('total_gols', 'sum'),
            partidas=('total_gols', 'count')
        ).reset_index()
        
        rodada = rodada.sort_values('rodada')
        return rodada
    
    # ─── TÁTICA ─────────────────────────────────────
    def estatisticas_taticas(self, time=None, ano=None):
        pass
    def _df_tatico(self):
    # Filtra apenas jogos com dados táticos completos
        colunas_taticas = [
            'escanteios_mandante', 'escanteios_visitante',
            'faltas_mandante', 'faltas_visitante',
            'chutes_mandante', 'chutes_visitante',
            'chutes_fora_mandante', 'chutes_fora_visitante',
            'defesas_mandante', 'defesas_visitante'
        ]
        return self.df.dropna(subset=colunas_taticas).copy()

    def eficiencia_ofensiva(self):
        df = self._df_tatico()
        
        # Combina mandante e visitante
        mandante = df[['time_mandante', 'gols_mandante', 'chutes_mandante']].rename(
            columns={'time_mandante': 'time', 'gols_mandante': 'gols', 'chutes_mandante': 'chutes'}
        )
        visitante = df[['time_visitante', 'gols_visitante', 'chutes_visitante']].rename(
            columns={'time_visitante': 'time', 'gols_visitante': 'gols', 'chutes_visitante': 'chutes'}
        )
        
        todos = pd.concat([mandante, visitante])
        
        eficiencia = todos.groupby('time').agg(
            total_gols=('gols', 'sum'),
            total_chutes=('chutes', 'sum'),
            jogos=('gols', 'count')
        ).reset_index()
        
        eficiencia['gols_por_jogo'] = (eficiencia['total_gols'] / eficiencia['jogos']).round(2)
        eficiencia['chutes_por_jogo'] = (eficiencia['total_chutes'] / eficiencia['jogos']).round(2)
        eficiencia['conversao_%'] = (eficiencia['total_gols'] / eficiencia['total_chutes'] * 100).round(1)
        
        return eficiencia.sort_values('conversao_%', ascending=False).reset_index(drop=True)

    def perfil_tatico(self, time):
        df = self._df_tatico()
        
        mandante = df[df['time_mandante'] == time]
        visitante = df[df['time_visitante'] == time]
        
        def media(mandante_col, visitante_col):
            return round(
                (mandante[mandante_col].sum() + visitante[visitante_col].sum()) /
                (len(mandante) + len(visitante)), 2
            )
        
        return {
            'Chutes':      media('chutes_mandante', 'chutes_visitante'),
            'Escanteios':  media('escanteios_mandante', 'escanteios_visitante'),
            'Faltas':      media('faltas_mandante', 'faltas_visitante'),
            'Defesas':     media('defesas_mandante', 'defesas_visitante'),
            'Chutes Fora': media('chutes_fora_mandante', 'chutes_fora_visitante'),
            'Impedimentos':media('impedimentos_mandante', 'impedimentos_visitante'),
        }

    def evolucao_tatica(self):
        df = self._df_tatico()
        
        evolucao = df.groupby('ano_campeonato').agg(
            media_chutes=('chutes_mandante', 'mean'),
            media_faltas=('faltas_mandante', 'mean'),
            media_escanteios=('escanteios_mandante', 'mean'),
            media_defesas=('defesas_mandante', 'mean')
        ).reset_index()
        
        # Soma mandante + visitante e divide por 2 para ter média por time por jogo
        df2 = df.groupby('ano_campeonato').apply(
            lambda g: pd.Series({
                'chutes_por_jogo': (g['chutes_mandante'].mean() + g['chutes_visitante'].mean()) / 2,
                'faltas_por_jogo': (g['faltas_mandante'].mean() + g['faltas_visitante'].mean()) / 2,
                'escanteios_por_jogo': (g['escanteios_mandante'].mean() + g['escanteios_visitante'].mean()) / 2,
                'defesas_por_jogo': (g['defesas_mandante'].mean() + g['defesas_visitante'].mean()) / 2,
            }), include_groups=False
        ).reset_index()
        
        return df2

    def desempenho_goleiros(self):
        df = self._df_tatico()
        
        mandante = df[['time_mandante', 'defesas_mandante', 'gols_visitante']].rename(
            columns={'time_mandante': 'time', 'defesas_mandante': 'defesas', 'gols_visitante': 'gols_sofridos'}
        )
        visitante = df[['time_visitante', 'defesas_visitante', 'gols_mandante']].rename(
            columns={'time_visitante': 'time', 'defesas_visitante': 'defesas', 'gols_mandante': 'gols_sofridos'}
        )
        
        todos = pd.concat([mandante, visitante])
        
        goleiros = todos.groupby('time').agg(
            total_defesas=('defesas', 'sum'),
            total_gols_sofridos=('gols_sofridos', 'sum'),
            jogos=('defesas', 'count')
        ).reset_index()
        
        goleiros['defesas_por_jogo'] = (goleiros['total_defesas'] / goleiros['jogos']).round(2)
        goleiros['gols_sofridos_por_jogo'] = (goleiros['total_gols_sofridos'] / goleiros['jogos']).round(2)
        
        return goleiros.sort_values('defesas_por_jogo', ascending=False).reset_index(drop=True)

    def correlacao_faltas_resultado(self):
        df = self._df_tatico()
        
        mandante = df[['time_mandante', 'faltas_mandante', 'resultado_mandante']].rename(
            columns={'time_mandante': 'time', 'faltas_mandante': 'faltas', 'resultado_mandante': 'resultado'}
        )
        visitante = df[['time_visitante', 'faltas_visitante', 'resultado_mandante']].copy()
        visitante['resultado'] = visitante['resultado_mandante'].map({
            'vitoria': 'derrota', 'derrota': 'vitoria', 'empate': 'empate'
        })
        visitante = visitante[['time_visitante', 'faltas_visitante', 'resultado']].rename(
            columns={'time_visitante': 'time', 'faltas_visitante': 'faltas'}
        )
        
        todos = pd.concat([mandante, visitante])
        
        correlacao = todos.groupby('resultado').agg(
            media_faltas=('faltas', 'mean'),
            total=('faltas', 'count')
        ).reset_index()
        
        correlacao['resultado'] = correlacao['resultado'].map({
            'vitoria': 'Vitória',
            'empate': 'Empate',
            'derrota': 'Derrota'
        })
        
        return correlacao