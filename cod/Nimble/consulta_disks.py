from nimbleclient import NimOSClient 
import pandas as pd
from datetime import datetime 

from argparse import ArgumentParser

parser = ArgumentParser(description="Consulta todos os dados dos HDs do Nimble",
                        usage="python consulta_disks.py --ip <IP_do_NIMBLE> --usuario <Nome_Usuário> --senha <Senha usada no Nimble>")
parser.add_argument('--ip', type=str, help="Ip do Storage Nimble")
parser.add_argument('--usuario', help='Nome do usuário cadastrado no Nimble')
parser.add_argument('--senha', help='Senha utilizada para acessar o Nimble')


class Disks_Nimble():
    def __init__(self, ip:str, username:str, senha:str) -> None:
        """
        Objeto criado para consultar os dados dos HD's dos Nimbles
        Parâmetros: ip -> ip do servidor
                    username -> usuário cadastrado no Nimble
                    senha -> senha cadastrada no Nimble
        
        Atributos: 
            self.attributes -> Dados dos atributos do Hd's ['name','Total LBAs written','Total LBAs flash writes',
            'Total Write Bytes Processed','Temperature C','Power on hours']
            self.pd_disk -> Dados dos HDs 

        Retorno: None

        Exemplo: 
            disks = Disks_Nimble('172.15.1.98', 'Teste', 'teste123')
            print(disks.pd_disk)
            print(disks.attributes)
        """
        api = NimOSClient(ip, username, senha)
        disks_list = api.disks.list()
        list_disks_id = [disks.id for disks in disks_list]
        
        list_series = []
        list_pd_disks = []
        self.list_all_smart_attribute = {}
        self.pd_attribute = pd.DataFrame()
        for id_disk in list_disks_id:
            data_disk = api.disks.get(id_disk).attrs
            if len(data_disk['smart_attribute_list']) > 0:
                slot = f"slot_{data_disk['slot']}"
                list_values = [slot]
                list_columns = ['name']
                for smart_attribute in data_disk['smart_attribute_list']:

                    list_values.append(smart_attribute['raw_value'])
                    list_columns.append(smart_attribute['name'])

                
                #list_series.append(pd.Series(data=list_values, index=list_columns, name=slot))
                list_series.append(pd.Series(data=list_values, index=list_columns))

            del data_disk['smart_attribute_list']
            del data_disk['id']
            del data_disk['array_id']
            del data_disk['shelf_id']

            pd_disk = pd.DataFrame.from_dict(data_disk, orient='index')
            pd_disk = pd_disk.T
            if pd_disk['state'].values == 'in use':
                pd_disk['bool_state'] = 1
            else:
                pd_disk['bool_state'] = 0
            
            pd_disk = pd_disk[['type', 'slot', 'bank', 'bool_state', 'state', 'size', 'model', 'serial', 'array_name',
            'is_dfc', 'shelf_serial', 'shelf_location', 'shelf_location_id', 'vshelf_id', 'raid_state', 
            'block_type', 'disk_internal_stat_1', 'path', 'vendor', 'firmware_version', 'hba', 'port',
            'raid_id', 'raid_resync_percent', 'raid_resync_current_speed', 'raid_resync_average_speed']]

            list_pd_disks.append(pd_disk)

        self.attributes = pd.DataFrame(list_series)
        self.attributes = self.attributes[['name','Total LBAs written','Total LBAs flash writes','Total Write Bytes Processed','Temperature C','Power on hours']]
        self.pd_disk = pd.concat(list_pd_disks)

def consulta_ip_nimble(nome_ip:str):
    """
    Função criada para identificar se o parâmetro IP é um ip ou o nome do host 
    Se for o nome do host, ele consulta o ip do host no arquivo /etc/hosts -> Linux

    Parâmetro: nome_ip -> IP ou Nome do Host

    Retorno: str -> IP do Nimble
                    ou 
             exit() -> Parâmetro IP errado

    Exemplo: ip_nimble = consulta_ip_nimble("NIMBLE")
    """
    if not nome_ip:
        exit()
    
    check_arg = nome_ip.split('.')
    check_arg = len(check_arg)
    if check_arg == 4:
        ip = nome_ip
        return ip
    elif check_arg == 1:
        hosts = open('/etc/hosts','r', encoding='iso-8859-1')
        for line in hosts:
            host = line.split()
            try:
                if host[3] == args.ip:
                    return host[0]
            except:
                pass
    else:
        print("Parâmetro IP errado")
        exit()


if __name__ == '__main__':
    """
    Função Principal, ao executar esse código será feito a consulta de todos os dados dos HDs, 
    transformará esses dados em DataFrame com pandas e depois retornará essas informações em texto separados por
    "Ponto e Virgula" ; para o zabbix conseguir consultar esses dados.  

    Exemplo: 
        python consulta_disks.py --ip '172.1.0.1' --usuario 'Teste' --senha 'Teste'
    """
    data_e_hora_atuais = datetime.now()
    data_e_hora_em_texto = data_e_hora_atuais.strftime('%d/%m/%Y %H:%M:%S') 
    args = parser.parse_args()
    ip_nimble = consulta_ip_nimble(args.ip)
    disk = Disks_Nimble(ip_nimble, args.usuario, args.senha)
    str_disks = "\n".join("; ".join(map(str, xs)) for xs in disk.pd_disk.itertuples(index=False))
    attributes_disks = "\n".join("; ".join(map(str, xs)) for xs in disk.attributes.itertuples(index=True))
    print(str_disks)
    print(attributes_disks)
    print(data_e_hora_em_texto)