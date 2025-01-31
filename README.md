# Backup dos Bancos de Dados (em Python)
Realiza um backup diário do mesmo gerado no servidor.

O seguro morreu de velho! Por mais que seja feito o backup do banco de dados no servidor, tanto os processos de exportação e compactação para que um BD de 3 Gb ocupe 500 Mb, ainda sim foi necessário ter uma segurança a mais. Os HD's de backup ficam conectados ao servidor e qualquer pane elétrica pode queimá-los. Como são alugados, decidi deixar um outro computador também realizando o mesmo backup: exportando e compactando os arquivos, para garantir uma maior segurança das informações. Como os scripts são executados no horário que estou almoçando, não atrapalham minha produtividade das atividades. Geralmente depois de um final de semana há mais backups para realizar o backup, assim sendo com uma velocidade de tráfego de rede setada para 100 kbps, continua sendo executada em segundo plano sem sobrecarregar o processamento do computador, uma vez que o utiliza o shell ao invés de componentes gráficos.
