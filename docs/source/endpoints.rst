Endpoints
=========

Abaixo estão listados os endpoints da API e seus detalhes.

================
Criar revendedor
================

Esse endpoint permite criar novos revendedores. É um endpoint aberto, ou seja, qualquer usuário pode criar sua conta.

--------------------
Endereço do endpoint
--------------------

Para acessar esse endpoint, utilizar o seguinte endereço: api/user/create-revendedor

-----------------------
Informações necessárias
-----------------------

Abaixo as informações necessárias para se criar um revendedor

======== ===========================
Campo    Especificações
======== ===========================
Email    Deve ser um email válido
Password Mínimo 8 caracteres
Cpf      Deve ser um CPF válido
Name     Obrigatório o preenchimento
======== ===========================

=====
Login
=====

Para acessar esse endpoint, utilizar o seguinte endereço: api/token

-----------------------
Informações necessárias
-----------------------

Abaixo as informações necessárias para realizar Login

======== ================
Campo    Especificações
======== ================
Email    Email cadastrado
Password Senha cadastrada
======== ================

-------
Retorno
-------

Como retorno de um login, o endpoint envia dois tokens

======== ================================================================
Token    Informações
======== ================================================================
Refresh  Token utilizado para gerar um novo token quando o Access expirar
Access   Token para garantir login (expirável)
======== ================================================================

=====================
Cadastrar nova compra
=====================

Para acessar esse endpoint, utilizar o seguinte endereço: api/cashback/cashback

-----------------------
Informações necessárias
-----------------------

Abaixo as informações necessárias para cadastrar nova compra

========== =====================================================
Campo      Especificações
========== =====================================================
Code       Código da compra (inteiro)
Value      Valor da compra (real)
Date       Data da compra
Revendedor Id do revendedor (não é campo obrigatório)
Status     Código do status da compra (não é campo obrigatório)
========== =====================================================

==============
Listar compras
==============

Para acessar esse endpoint, utilizar o seguinte endereço: api/cashback/cashback

------------------------
Informações apresentadas
------------------------

Abaixo as informações apresentadas para cada compra

================ ====================================================
Campo            Especificações
================ ====================================================
Id               Id da compra
Code             Código da compra (inteiro)
Value            Valor da compra (real)
Date             Data da compra
Revendedor       Id do revendedor
Status           Código do status da compra
Cashback_percent % de cashback aplicado para essa compra
Cashback_value   Valor de cashback aplicado para essa compra
Status_str       Status da compra (em formato texto)
================ ====================================================


============================
Exibir acumulado de cashback
============================

Para acessar esse endpoint, utilizar o seguinte endereço: api/cashback/cashback/accumulated-cashback/?cpf=<CPF>

-----------------------
Informações necessárias
-----------------------

É preciso informar o CPF do revendedor.

------------------------
Informações apresentadas
------------------------

Abaixo as informações apresentadas para o cashback acumulado

====== ======================================================
Campo  Informações
====== ======================================================
Credit Total de créditos de cashback acumulados até o momento
====== ======================================================
