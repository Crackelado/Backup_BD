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
# Ao utilizar "{}" no texto, pode ser substituído por outro
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

# Inverte a lista para começar dos arquivos mais antigos primeiro
lista.reverse()

# Loop para percorrer nome dos arquivos do array
for i in lista:
	
	# Realizar o processo de backup, apenas dos arquivos inexistentes e limita o tráfego à 100 kbps ("--bwlimit=100")
    	run(['rsync', '-vh', '-u', '--progress', '--bwlimit=100', i, atalho])

	# Apaga arquivo do computador da rede que realiza backup para não encher HD
    	run(['rm', i])

# Variável que cria um array de todos os arquivos salvos na pasta backup/local. Possui o mesmo nome da variável anterior e, como os dados de antes não serão utilizados mais durante o script, ela é reaproveitada para liberar espaço na memória
lista = listar(atalho)

# Variável para armazenar a quantidade de arquivos no array "lista"
contador = len(lista)

# Variável para armazenar array com as datas, que se econtram no nome dos arquivos de backup, na quantidade de 30 registros
lista2 = [s.split('_')[1].split('-')[0] for s in lista[:30]]

# Modifica a variável de array para texto e armazena todas as datas
lista2 = ''.join(lista2)

# Variável para armazenar array de todos os arquivos salvos na pasta backup/servidor
temp = listar('/mnt/tmp', tempo='')

# Realiza o filtro para obter somente as datas, transformando em outro array com quantidade de 20 registros
temp = [s.split('_')[1].split('-')[0] for s in temp[:20]]

# Pegar a lista somente dos que não foram feito os backups
temp2 = [s for s in temp if s not in lista2]

# Inverte o array para começar a realizar o backup dos mais antigos primeiro
temp2.reverse()

# Redefine variável para reaproveitamento
temp = []

# Loop para realizar o processo de backup, apenas dos arquivos inexistentes
for i in temp2:

	# Comando que realiza backup com limite de tráfego de rede a 100 kbps. Substitui as "{}" pela data do loop
	run(['rsync', '-vh', '-u', '--progress', '--bwlimit=100', atalho3.format(i), atalho])

	# Aumenta quantidade da variável para ser utilizada no arquivo ".log"
	contador += 1

# Redefine variável com lista de todos os arquivos salvos no backup/local
lista = listar(atalho)

# Abre o arquivo ".log", como somente leitura, e associa com a variável. Quando aberto não pode ser manipulado por outro programa
f = open(log, 'r')

# Faz a leitura das linhas do arquivo e joga na variável array
r = f.readlines()

# Fecha arquivo para que possa ser editado por outros programas
f.close()

# Acrescenta na variável array, como primeiro registro, a data do terminal shell adquirida anteriormente, acrescido de símbolo de quebra de linha ("\n")
temp.append(dataText.stdout.decode('utf-8').split('\n')[0] + '\n')

# Loop para percorrer array em apenas 30 registros
for i in lista[:30]:

	# Se o arquivo que foi feito o backup tiver a mesma data do dia, é acrescentado no array
    	if data in i:

		# Acrescenta no array nome do arquivo acrescido de símbolo de quebra de linha ("\n")
		temp.append(i + '\n')

# Acrescenta no array mensagem de finalização do backup e símbolo de quebra de linha ("\n")
temp.append(echo + '\n')

# Acrescenta no array a quantidade de arquivos que foram copiados ("{}" <> contador).
temp.append('A quantidade de arquivos de backups já salvos é de: {} rar\'s'.format(contador) + '\n\n')

# Subsitui a variável pelos dados uso do HD de backup/local
lista = run(['df', '-h', atalho], stderr=PIPE, stdout=PIPE)

# Acrescenta dados, de uso do HD de backup/local, no array
temp += lista.stdout.decode('utf-8')

# Acrescenta no array símbolo de quebra de linha ("\n")
temp.append('\n')

# Acrescenta dados antigos do arquivo ".log", fazendo que apareça depois dos dados atuais
temp += r

# Abre o arquivo ".log", como escrita, e associa com a variável. Quando aberto não pode ser manipulado por outro programa 
f = open(log, 'w')

# Faz a gravação das linhas do arquivo de log
f.writelines(temp)

# Fecha arquivo para que possa ser editado por outros programas
f.close()

# Desmonta as unidades
run(['umount', '/mnt/backup'])
run(['umount', '/mnt/banco'])
run(['umount', '/mnt/tmp'])
