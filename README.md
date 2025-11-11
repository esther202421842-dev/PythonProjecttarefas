Mini Gestor de Tarefas, Sprint 1

Disciplina: Laboratório de Engenharia de Software  
 Aluna: Esther Carvallo  
 Professora: Aline  
 Sprint 1— Outubro/2025  

Objetivo do Sprint 1
Criar a estrutura inicial de um sistema de gerenciamento de tarefas utilizando Python e SQLite, 
seguindo os princípios de Engenharia de Software com documentação e versionamento apropriados.

Funcionalidades Implementadas
Nesta primeira entrega, foram desenvolvidos:

- Criar tarefa   
- Listar tarefas registradas  
- Editar tarefa 
- Excluir tarefa   
- Marcar tarefa como concluída   
- Persistência de dados em banco SQLite
- Menu interativo em CLI (linha de comando)

Todos os dados são salvos automaticamente no arquivo `todo.db`, garantindo que as informações não sejam perdidas ao fechar o sistema.


 Requisitos contemplados

 Requisitos Funcionais
RF01: O sistema deve permitir cadastrar novas tarefas  
RF02: O sistema deve permitir listar tarefas existentes  
RF03: O sistema deve permitir editar tarefas  
RF04: O sistema deve excluir tarefas  
RF05: O sistema deve permitir marcar tarefas como concluídas  

Requisitos Não Funcionais
RNF01: O sistema deve armazenar as informações em banco de dados SQLite  
RNF02:O sistema deve possuir interface em linha de comando (CLI)  
RNF03: Os dados devem persistir após encerramento do programa  


 Tecnologias Utilizadas

 Ferramenta | Utilização 
----------- |-----------|
| Python    | Lógica do sistema 
| SQLite3   | Banco de dados 
| PyCharm   | Desenvolvimento e execução 
| Git & GitHub | Versionamento de código 


 Diagramas Produzidos
- Diagrama de Casos de Uso
- Diagramas de Sequência
- Descrição completa dos Casos de Uso
- Requisitos funcionais e não funcionais documentados







Sprint 2 – Mini Gestor de Tarefas

Nesta segunda etapa do projeto, foram implementadas funcionalidades avançadas de busca e filtragem.

Funcionalidades Entregues – Sprint 2

Filtrar tarefas por status  
Filtrar tarefas por tag 
Filtrar tarefas por prioridade  
Combinação de filtro  
Busca por palavra-chave  
Melhorias no menu e validação de dados  
Atualização dos diagramas UML


 Requisitos Funcionais – Sprint 2

RF07 – Filtrar por Status
O sistema deve permitir que o usuário filtre tarefas por *todo*, *doing* ou *done*.

RF08 – Filtrar por Tag
O sistema deve listar tarefas que contenham uma ou mais tags informadas.

RF09 – Filtrar por Prioridade
O usuário pode exibir apenas tarefas de prioridade:
- 1 = Alta  
- 2 = Média  
- 3 = Baixa  

RF10 – Combinação de Filtros
O sistema deve permitir que o usuário aplique mais de um filtro ao mesmo tempo, como:
- status + prioridade  
- tag + prioridade  
- status + palavra-chave  
- todos os filtros juntos  

RF11 – Busca por Palavra-Chave
O usuário pode buscar tarefas digitando um termo que será procurado em:
- título  
- descrição  
- tags


  Requisitos Não Funcionais – Sprint 2

RNF04 – Persistência Aprimorada
O banco SQLite deve armazenar corretamente novos campos e permitir filtros combinados.

RNF05 – Validação de Dados
O sistema deve validar:
- status informado  
- prioridade válida (1, 2 ou 3)  
- tags no formato CSV  
- palavra-chave não vazia  

RNF06 – Documentação Atualizada
Todos os seguintes artefatos devem ser atualizados:
- casos de uso  
- diagramas de sequência  
- diagramas de atividade 

  


Diagramas UML do Sprint 2

 Diagrama de Caso de Uso – Filtros e Busca  
 Diagrama de Sequência – Listagem com Filtros  
 Diagrama de Sequência – Busca por Palavra-Chave  
 Diagrama de Atividade – Listagem Filtrada  
 Diagrama de Atividade – Busca por Palavra-Chave  

*(As imagens estão incluídas no repositório.)*

 Status do Sprint 2
 Concluído com sucesso


