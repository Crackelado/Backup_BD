#! python3.10

# Importa as classes "run" e "PIPE" do módulo "subprocess", responsável para importar consultas feitas no terminal linux (shell) e passar para variável
from subprocess import run, PIPE

# Importa classe "datetime" do módulo "datetime", responsável para pegar datas e transformar em texto conforme necessário
from datetime import datetime

# Função realizar pesquisa de arquivo de backup
# As "caminho" (pasta para pesquisar), "tempo" (acrescenta atributos na pesquisa de data e hora antes do nome do arquivo) e "caminho_comp" (acrescenta o restante do atalho pois, ao pesquisar, mostra somente o nome do arquivo)
def listar(caminho, tempo='--full-time', caminho_comp=''):

	# Realiza pesquisa na pasta específica
	# Complemento "-t" é utilizado para ordenar os arquivos dos criados recentemente
    	grupo = run(['ls', '-t', tempo, caminho], stderr=PIPE, stdout=PIPE)

	# Converte os dados da pesquisa em texto e transforma em um array, com o indicador de quebra de linha como final do texto ("\n")
    	grupo = grupo.stdout.decode('utf-8').split('\n')

	# Loop que pega somente arquivos com extensão ".rar". É acrescentado o caminho completo da pasta antes do nome do arquivo
    	grupo = [caminho_comp + s for s in grupo if '.rar' in s]

	# Função devolve um array com origem de onde estão os arquivos
    	return grupo

# Variável que armazena texto de término, com quebra de linha ("\n"), para escrita no arquivo ".log"
echo = 'Backup concluído!\n'

# Variável para armazenar caminho do arquivo ".log"
log = '/home/usuario/Documents/Luiz2023/Automacao/automacao.log'

# Variável para armazenar todos os dados da data atual (mês, dia, ano, ...), que é representada no terminal shell
dataText = run(['date'], stderr=PIPE, stdout=PIPE)

# Variável para armazenar a data atual (%ano(4 dígitos)-%mês-%dia)
data = datetime.today().strftime('%Y-%m-%d')

# Variável para armazenar caminho de onde serão salvos os arquivos de backup, já mapeados no computador
atalho = '/mnt/backup/bkp SPData/novo'

# Variável para armazenar caminho dos arquivos de backup do servidor, já mapeados no computador
atalho2 = '/mnt/banco/'

# Variável para armazenar caminho dos arquivos de backup gerado por outro computador na rede, já mapeados no computador
" Ao utilizar "{}" no texto, pode ser substituído acrescentando uma formatação
atalho3 = '/mnt/tmp/sghspdata1962_{}-2000.rar'

# Criar pastas para montar pastas de rede e local, caso não existam
run(['mkdir', '/mnt/backup'])
run(['mkdir', '/mnt/banco'])
run(['mkdir', '/mnt/tmp'])

# Montar unidades de rede ou partição local
run(['mount', '-t', 'cifs', '//10.150.200.19/banco', '/mnt/banco', '-o', 'username=****,password=****,iocharset=utf8'])
run(['mount', '-t', 'ntfs-3g', 'UUID=98921C06921BE790', '/mnt/backup'])
run(['mount', '-t', 'cifs', '//10.150.200.4/c$/banco/backup', '/mnt/tmp', '-o', 'username=****,password=****,iocharset=utf8'])

# Cria um array de todos os backups realiados pelo computador da rede
lista = listar(atalho2, tempo='', caminho_comp=atalho2)

# 
lista.reverse()

# Realizar o processo de backup, apenas dos arquivos inexistentes
for i in lista:
    run(['rsync', '-vh', '-u', '--progress', '--bwlimit=100', i, atalho])
    run(['rm', i])

# Captura uma lista de todos os arquivos salvos na pasta backup/local
lista = listar(atalho)
contador = len(lista)
lista2 = [s.split('_')[1].split('-')[0] for s in lista[:30]]
lista2 = ''.join(lista2)

# Captura uma lista de todos os arquivos salvos na pasta backup/servidor
temp = listar('/mnt/tmp', tempo='')
temp = [s.split('_')[1].split('-')[0] for s in temp[:20]]

# Pegar a lista somente dos que não foram feito os backups
temp2 = [s for s in temp if s not in lista2]
temp2.reverse()
temp = []

# Realizar o processo de backup, apenas dos arquivos inexistentes
for i in temp2:
	run(['rsync', '-vh', '-u', '--progress', '--bwlimit=100', atalho3.format(i), atalho])
	contador += 1

lista = listar(atalho)

# Abrir o arquivo de log para escrever a saída do backup
f = open(log, 'r')
r = f.readlines()
f.close()
temp.append(dataText.stdout.decode('utf-8').split('\n')[0] + '\n')

for i in lista[:30]:
    if data in i:
        temp.append(i + '\n')
        
temp.append(echo + '\n')
temp.append('A quantidade de arquivos de backups já salvos é de: {} rar\'s'.format(contador) + '\n\n')
lista = run(['df', '-h', atalho], stderr=PIPE, stdout=PIPE)
temp += lista.stdout.decode('utf-8')
temp.append('\n')
temp += r
f = open(log, 'w')
f.writelines(temp)
f.close()

# Desmontar unidades
run(['umount', '/mnt/backup'])
run(['umount', '/mnt/banco'])
run(['umount', '/mnt/tmp'])
