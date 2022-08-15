from nimbleclient import NimOSClient 
import pandas as pd
from argparse import ArgumentParser
from datetime import datetime 


parser = ArgumentParser(description="Consulta todos os dados das controladoras do Nimble",
                        usage="python consulta_controllers.py --ip <IP_do_NIMBLE> --usuario <Nome_Usuário> --senha <Senha usada no Nimble>")
parser.add_argument('--ip', type=str, help="Ip do Storage Nimble")
parser.add_argument('--usuario', help='Nome do usuário cadastrado no Nimble')
parser.add_argument('--senha', help='Senha utilizada para acessar o Nimble')

list_sensors_temperture = ['inlet-temp', 'outlet-temp', 'LeftEar', 'bp-temp', 'inlet-temp', 'outlet-temp', 'bp-temp', 'RightEar']

class Controllers_Nimble():
    
    def __init__(self, ip:str, usuario:str, senha:str) -> None:
        """
        Objeto criado para consultar os dados das controladoras
        Parâmetros: ip -> ip do servidor
                    username -> usuário cadastrado no Nimble
                    senha -> senha cadastrada no Nimble
        
        Atributos: 
            self.pd_fan -> Dados de todas as FAN's
            self.pd_power_supplies -> Dados de todas as Fontes de Energia
            self.pd_temperature_sensors -> Dados de todos os sensores de Temperatura
            self.pd_partition_status -> Dados de todas as partições
            self.pd_controllers ->  Status geral de todos os sensores e dados das controladoras

        Retorno: None

        Exemplo: 
            controllers = Controllers_Nimble('172.15.1.98', 'Teste', 'teste123')
            print(controllers.pd_fan)
            print(controllers.pd_power_supplies)
        """
        api = NimOSClient(ip, usuario, senha)
        controllers_list = api.controllers.list()
        list_id_controllers = [controller.id for controller in controllers_list]
        list_controllers = ['fans', 'temperature_sensors', 'partition_status']

        list_fan = []
        list_power_supplies = []
        list_temperature_sensors = []
        list_partition_status = []

        list_controllers = []
        for id_controller in list_id_controllers:
            data_controller = api.controllers.get(id_controller).attrs
            dict_controllers = {}
            for k, v in data_controller.items():
                
                if k in 'fans':           
                    for fan in v:
                        pd_fan = pd.DataFrame.from_dict(fan, orient='index')
                        pd_fan = pd_fan.T
                        pd_fan['controladora'] = data_controller['name']
                        pd_fan['tipo'] = 'pd_fan'
                        list_fan.append(pd_fan)
                    
                elif k in 'power_supplies':    
                    for power_supplies in v:
                        pd_power_supplies = pd.DataFrame.from_dict(power_supplies, orient='index')
                        pd_power_supplies = pd_power_supplies.T
                        pd_power_supplies['controladora'] = data_controller['name']
                        pd_power_supplies['tipo'] = 'pd_power_supplies'
                        list_power_supplies.append(pd_power_supplies)

                elif k in 'temperature_sensors':    
                    for temperature_sensors in v:
                        pd_temperature_sensors = pd.DataFrame.from_dict(temperature_sensors, orient='index')
                        pd_temperature_sensors = pd_temperature_sensors.T
                        pd_temperature_sensors['controladora'] = data_controller['name']
                        pd_temperature_sensors['tipo'] = 'pd_temperature_sensors'
                        list_temperature_sensors.append(pd_temperature_sensors)

                elif k in 'partition_status':    
                    for partition_status in v:
                        pd_partition_status = pd.DataFrame.from_dict(partition_status, orient='index')
                        pd_partition_status = pd_partition_status.T
                        pd_partition_status['controladora'] = data_controller['name']
                        pd_partition_status['tipo'] = 'partition_status'
                        list_partition_status.append(pd_partition_status)

                else:
                    dict_controllers[k] = v

            pd_controllers = pd.DataFrame.from_dict(dict_controllers, orient='index')
            pd_controllers = pd_controllers.T
            pd_controllers['controladora'] = data_controller['name']

            # Conversão dos status de str para int, para criar uma trigger no Zabbix
            if pd_controllers['temperature_status'].values[0] == 'temperature_okay':
                pd_controllers['temperature_status'] = 1
            else:
                pd_controllers['temperature_status'] = 0

            if pd_controllers['fan_status'].values[0] == 'fan_okay':
                pd_controllers['fan_status'] = 1
            else:
                pd_controllers['fan_status'] = 0

            if pd_controllers['power_status'].values[0] == 'ps_okay':
                pd_controllers['power_status'] = 1
            else:
                pd_controllers['power_status'] = 0
            
            pd_controllers['tipo'] = 'controllers'
            list_controllers.append(pd_controllers)

        self.pd_fan = pd.concat(list_fan)
        self.pd_power_supplies = pd.concat(list_power_supplies)
        self.pd_temperature_sensors = pd.concat(list_temperature_sensors)
        self.pd_partition_status = pd.concat(list_partition_status)
        self.pd_controllers = pd.concat(list_controllers)


def consulta_ip_nimble(nome_ip:str) -> str:
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
    Função Principal, ao executar esse código será feito a consulta de todos os dados das controladoras, 
    transformará esses dados em DataFrame com pandas e depois retornará essas informações em texto separados por
    "Ponto e Virgula" ; para o zabbix conseguir consultar esses dados.  

    python consulta_disks.py --ip '172.1.0.1' --usuario 'Teste' --senha 'Teste'
    """
    data_e_hora_atuais = datetime.now()
    data_e_hora_em_texto = data_e_hora_atuais.strftime('%d/%m/%Y %H:%M:%S') 
    args = parser.parse_args()
    ip_nimble = consulta_ip_nimble(args.ip)
    controllers = Controllers_Nimble(ip_nimble, args.usuario, args.senha)
    fans = "\n".join("; ".join(map(str, xs)) for xs in controllers.pd_fan.itertuples(index=False))
    power_supplies = "\n".join("; ".join(map(str, xs)) for xs in controllers.pd_power_supplies.itertuples(index=False))
    temperature_sensors = "\n".join("; ".join(map(str, xs)) for xs in controllers.pd_temperature_sensors.itertuples(index=False))
    partition_status = "\n".join("; ".join(map(str, xs)) for xs in controllers.pd_partition_status.itertuples(index=False))
    controllers_txt = "\n".join("; ".join(map(str, xs)) for xs in controllers.pd_controllers.itertuples(index=False))
    print(fans)
    print(power_supplies)
    print(temperature_sensors)
    print(partition_status)
    print(controllers_txt)
    print(data_e_hora_em_texto)