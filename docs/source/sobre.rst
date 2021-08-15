Sobre
=====

**cashback** é um desafio encontrado no **Grupo Boticário**

=====================
Problema/Oportunidade
=====================
O Boticário tem várias soluções para ajudar seus revendedores(as) a gerir suas finanças e alavancar suas vendas. Também existem iniciativas para impulsionar as operações de vendas como metas gameficadas e desconto em grandes quantidades de compras.

Agora queremos criar mais uma solução, e é aí que você entra com seu talento ;)

A oportunidade proposta é criar um sistema de Cashback, onde o valor será disponibilizado como crédito para a próxima compra da revendedora no Boticário;

Cashback quer dizer “dinheiro de volta”, e funciona de forma simples: o revendedor faz uma compra e seu benefício vem com a devolução de parte do dinheiro gasto no mês seguinte.

Sendo assim o Boticário quer disponibilizar um sistema para seus revendedores(as) cadastrarem suas compras e acompanhar o retorno de cashback de cada um.

==========
Requisitos
==========
* Rota para cadastrar um novo revendedor(a) exigindo no mínimo nome completo, CPF, e- mail e senha;
* Rota para validar um login de um revendedor(a);
* Rota para cadastrar uma nova compra exigindo no mínimo código, valor, data e CPF do revendedor(a). Todos os cadastros são salvos com o status “Em validação” exceto quando o CPF do revendedor(a) for 153.509.460-56, neste caso o status é salvo como “Aprovado”;
* Rota para listar as compras cadastradas retornando código, valor, data, % de cashback aplicado para esta compra, valor de cashback para esta compra e status;
* Rota para exibir o acumulado de cashback até o momento, essa rota irá consumir essa informação de uma API externa disponibilizada pelo Boticário. 

============
Casos de Uso
============
Os critérios de bonificação são:

* Para até 1.000 reais em compras, o revendedor(a) receberá 10% de cashback do valor vendido no período de um mês (sobre a soma de todas as vendas);

* Entre 1.000 e 1.500 reais em compras, o revendedor(a) receberá 15% de cashback do valor vendido no período de um mês (sobre a soma de todas as vendas);

* Acima de 1.500 reais em compras, o revendedor(a) receberá 20% de cashback do valor vendido no período de um mês (sobre a soma de todas as vendas).