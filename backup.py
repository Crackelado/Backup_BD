#! python3.10

from subprocess import run, PIPE
from datetime import datetime

# Função realizar pesquisa
def listar(caminho, tempo='--full-time', caminho_comp=''):
    grupo = run(['ls', '-t', tempo, caminho], stderr=PIPE, stdout=PIPE)
    grupo = grupo.stdout.decode('utf-8').split('\n')
    grupo = [caminho_comp + s for s in grupo if '.rar' in s]

    return grupo

echo = 'Backup concluído!\n'
log = '/home/usuario/Documents/Luiz2023/Automacao/automacao.log'
dataText = run(['date'], stderr=PIPE, stdout=PIPE)
data = datetime.today().strftime('%Y-%m-%d')
atalho = '/mnt/backup/bkp SPData/novo'
atalho2 = '/mnt/banco/'
atalho3 = '/mnt/tmp/sghspdata1962_{}-2000.rar'

# Criar pastas para montar pastas de rede e local, caso não existam
run(['mkdir', '/mnt/backup'])
run(['mkdir', '/mnt/banco'])
run(['mkdir', '/mnt/tmp'])

# Montar unidades de rede ou partição local
run(['mount', '-t', 'cifs', '//10.150.200.19/banco', '/mnt/banco', '-o', 'username=adm,password=vacatuça,iocharset=utf8'])
run(['mount', '-t', 'ntfs-3g', 'UUID=98921C06921BE790', '/mnt/backup'])
run(['mount', '-t', 'cifs', '//10.150.200.4/c$/banco/backup', '/mnt/tmp', '-o', 'username=ti03,password=ti3991,iocharset=utf8'])

# Apagar todos os backups para não encher HD do Painel
lista = listar(atalho2, tempo='', caminho_comp=atalho2)
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
