import pandas as pd
import numpy as np
from utils import *
from relatorio import *

""" 
TR -> Tempo de Relógio da Simulação
ES -> Estado do Servidor
HC -> Ocorrência do Próximo Evento de Chegada
HS -> Tempo de ocorrência do Próximo Evento de Saída
TF -> Tamanho da Fila
"""

def processa_chegada(df_tec, rnd_tec, df_ts, rnd_ts, queue_limit, TR, ES, TF, HC, HS):
    TR = HC  # atualiza relóogio para próxima chegada

    if ES == 0:  # servidor ocioso
        ES = 1
        TS = gera_tempo_servico(df_ts, rnd_ts)

        HS = TR + TS  # agenda a próxima saída

    else:
        # Fila sem limites
        if queue_limit == np.inf:
            TF += 1  # atualiza tamanho da fila
        
        else:
            if TF < queue_limit:
                TF += 1

    
    # gera próxima chegada e agenda ela
    TEC = gera_tempo_chegada(df_tec, rnd_tec)

    HC = TR + TEC

    return (TR, ES, TF, HC, HS)


def processa_saida(df_ts, rnd_ts, TR, ES, TF, HC, HS):
    TR = HS  # atualiza o relógio para próxima saída

    if TF > 0:
        TF -= 1  # atualiza tamanho da fila

        TS = gera_tempo_servico(df_ts, rnd_ts)

        HS = TR + TS

    else:
        ES = 0

        # agenda uma saída fictícia
        HS = np.inf
    
    return (TR, ES, TF, HC, HS)


def gera_tempo_servico(df, rnd = True):
    if rnd == True:  # aleatório
        random_number = np.random.uniform()

        # procura o intervalo correspondente
        intervals = df.iloc[:, 3]

        for i, interval in enumerate(intervals):
            if random_number >= interval[0] and random_number <= interval[1]:
                idx_interval = i
        
        # usa a classe correspondente para obter o ponto médio
        classes = df.iloc[:, 0]
        c = classes[idx_interval]

        ts = sum(c)/2
    else:  # determinístico
        classes = df.iloc[:, 0]
        c = classes[0]

        ts = sum(c)/2
    
    return ts


def gera_tempo_chegada(df, rnd = True):
    if rnd == True:  # aleatório
        random_number = np.random.uniform()

        # procura o intervalo correspondente
        intervals = df.iloc[:, 3]

        for i, interval in enumerate(intervals):
            if random_number >= interval[0] and random_number <= interval[1]:
                idx_interval = i
        
        # usa a classe correspondente para obter o ponto médio
        classes = df.iloc[:, 0]
        c = classes[idx_interval]

        tec = sum(c)/2
    else:  # determinístico
        classes = df.iloc[:, 0]
        c = classes[0]

        tec = sum(c)/2
    
    return tec


def simulacao(df_tec, df_ts, rnd_tec, rnd_ts, queue_limit, max_event):
    TR, ES, TF, HC = 0, 0, 0, 0
    HS = np.inf

    # gera dataframe da simulação
    cols = ['Evento', 'Cliente', 'TR', 'ES', 'TF', 'HC', 'HS']
    initial_row = ['Início', '_', TR, ES, TF, HC, HS]

    df2 = pd.DataFrame([initial_row], columns=cols)

    clients = []
    client_id = 0

    # para casos de fila com limite
    quit_clients = []  # clientes que foram embora porque a fila estava cheia

    event = 0

    while(event < max_event):
        if HC < HS:  # deve processar chegada
            client_id += 1
            clients.append(client_id)  # coloca cliente no sistema

            TR, ES, TF, HC, HS = processa_chegada(df_tec, rnd_tec, df_ts, rnd_ts, queue_limit, TR, ES, TF, HC, HS)

            # adiciona nova informação no DataFrame
            new_row = {'Evento':'Chegada', 'Cliente':client_id, 'TR':TR, 'ES':ES, 'TF':TF, 'HC':HC, 'HS':HS}
            df2 = df2.append(new_row, ignore_index=True)

            # trata casos de fila com limite
            # evento anterior a chegada atual era uma chegada e a fila estava no tamanho máximo
            if (queue_limit != np.inf) and (df2['TF'].iloc[-2] == queue_limit):
                removed_client = clients.pop() # remove cliente do sistema

                quit_clients.append(removed_client)

                # adiciona nova informação no DataFrame
                new_row = {'Evento':'Saída', 'Cliente':removed_client, 'TR':TR, 'ES':ES, 'TF':TF, 'HC':HC, 'HS':HS}
                df2 = df2.append(new_row, ignore_index=True)

        else:
            removed_client = clients.pop(0) # remove cliente do sistema

            TR, ES, TF, HC, HS = processa_saida(df_ts, rnd_ts, TR, ES, TF, HC, HS)

            # adiciona nova informação no DataFrame
            new_row = {'Evento':'Saída', 'Cliente':removed_client, 'TR':TR, 'ES':ES, 'TF':TF, 'HC':HC, 'HS':HS}
            df2 = df2.append(new_row, ignore_index=True)
        
        event += 1


    if queue_limit != np.inf:
        # retorna o dataframe e a lista de possíveis clientes que foram embora sem atendimento
        return df2, quit_clients
    
    # para casos sem limite na fila, retorna apenas o dataframe da simulação
    return df2


if __name__ == '__main__':
    max_event = int(input('Digite um número máximo de eventos para a simulação: '))
    
    op1 = input('\nO valor do Tempo entre Chegadas (TEC) é determinístico? [y/n] ').lower()
    
    if op1 == 'y':
        rnd_tec = False  # flag que demarca que TEC é determinístico
        
        f = float(input('Qual o valor do Tempo entre chegadas (TEC): '))
        f = [f*2]
    else:
        rnd_tec = True  # TEC aleatório

        filename = input('Insira nome do arquivo do TEC: ')
        f = read_csv(filename)
    
    op2 = input('\nO valor do Tempo de Serviço (TS) é determinístico? [y/n] ').lower()
    
    if op2 == 'y':
        rnd_ts = False  # TS determinístico

        f2 = float(input('Qual o valor do Tempo de Serviço (TS): '))
        f2 = [f2*2]
    else:
        rnd_ts = True  # TS Aleatório

        filename2 = input('Insira nome do arquivo do TS: ')
        f2 = read_csv(filename2)
    
    # Trata casos de fila com e sem limite
    op3 = input('\nA fila tem limite? [y/n] ').lower()
    
    if op3 == 'y':
        queue_limit = int(input('Qual o limite da fila? '))
    else:
        queue_limit = np.inf  # fila sem limite
    
    
    # trata os dados
    data = remove_outliers(f)

    # gera tabela usando o MMC
    df = mmc(data)
    print('\n\nFrequências e valores empregados no MMC para TEC:')
    print(f'{df.to_string(index=False)}\n')


    data2 = remove_outliers(f2)

    df2 = mmc(data2)
    print('\nFrequências e valores empregados no MMC para TS:')
    print(f'{df2.to_string(index=False)}\n')

    # realiza Simulação
    # trata dois tipos de simulação (com limite de fila e sem limite)
    if queue_limit == np.inf:
        simulation = simulacao(df, df2, rnd_tec, rnd_ts, queue_limit, max_event)
    else:
        simulation, quit_clients = simulacao(df, df2, rnd_tec, rnd_ts, queue_limit, max_event)
    
    print('\n\nTabela de simulação:')
    print(f'{simulation.to_string(index=False)}\n')

    # caso a simulação tenha limite de fila
    if queue_limit != np.inf:
        if len(quit_clients) > 0:
            if len(quit_clients) == 1:
                print(f'\nO cliente {quit_clients[0]} foi embora pois a fila estava cheia.')
            else:
                print(f'\nOs clientes {quit_clients} foram embora pois a fila estava cheia.')

    # gera relatório da simulação
    print('\nRelatório Final:')
    media_entidades_na_fila(simulation)
    ocupacao_dos_servidores(simulation)
    tempo_medio_fila(simulation)
    tempo_medio_sistema(simulation)
