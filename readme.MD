# Implémentation d'une application de la blockchain en python

Implémentation d'un système monétaire distribué et fermé grâce à la Blockchain


## Installation

Différentes dépendances sont nécessaire au bon fonctionnement de l'application

- Flask (framework dév web), pour la communication des noeuds
```bash
pip install flask
pip install -u flask-cors
```

- Requests, la librairie HTTP
```bash
pip install requests
```

- Pycrytpo, pour les fonctions de hash
```bash
pip install pycryptodome
```

Afin de pouvoir tester les fonctions de l'API, il vous faut télécharger un logiciel permettant d'envoyer et de recevoir des requêtes HTTP. Dans mon cas, j'ai utilisé [Postman](https://www.getpostman.com/).


## Usage

Le programme fonctionne sous Python3
Dans un terminal, lancer la commande suivante:

`python node.py -p [port]`

Cette commande doit être lancé sur plusieurs terminaux afin de créer un réseau de noeuds (sur des ports différents)

Exemple:
```
python node.py -p 8000
python node.py -p 8001
```
Info: En l'absence de port, le noeud se lance sur le port 8000.

### Listes des appels
#### [Requêtes GET]
`/blockchain` retourne la blockchain actuelle

`/nodes` retourne la liste des noeuds connus

`/current_transactions` retourne la liste des transactions en cours (non validées)

`/wallet` retourne les clés (publique/privé) ainsi que le solde actuel du noeud

#### [Requêtes POST]
`/mine` pour miner le bloc actuel

`/create_transaction` pour créer une transaction avec les données JSON `{"receiver":"pub_key", "amount":0}`

`/node` pour ajouter un noeud à la liste de noeuds connus avec les données JSON `{"node":"localhost:xxxx"}`


## Scénario
Noeud 8000
```
>> python node.py -p 8000
```
Noeud 8001
```
>> python node.py -p 8001
```

Création de Wallet (clés publiques/privées) pour chaque noeuds
```
>> Requete GET localhost:8000/wallet
>> Requete GET localhost:8001/wallet
```
![image](/images/wallet.png?raw=true)
___
Ajout des noeuds voisins
```
>> Requete POST localhost:8000/add_node avec JSON {"node":"localhost:8001"}
>> Requete POST localhost:8001/add_node avec JSON {"node":"localhost:8000"}
```
![image](/images/add_node.PNG?raw=true)
___
Création d'une transaction sur le noeud 8000
```
>> Requete POST localhost:80000/create_transaction avec JSON {"receiver":"PUBLIC_KEY", amount: 0}
```
![image](/images/create_transac.PNG?raw=true)
___
Visionnage des transactions en cours pour chaque noeuds
```
>> Requete GET localhost:8000/current_transactions
>> Requete GET localhost:8001/current_transactions
```
![image](/images/current_transacs.PNG?raw=true)
___
Noeud 8001 mine le bloc courant
```
>> Requete POST localhost:8001/mine
```
![image](/images/mine.PNG?raw=true)
___
Visionnage de la blockchain de chaque noeuds
```
>> Requete GET localhost:8000/blockchain
>> Requete GET localhost:8001/blockchain
```
![image](/images/blockchain.PNG?raw=true)
___
Visionnage des transactions en cours après minage du bloc
```
>> Requete GET localhost:8000/current_transactions
>> Requete GET localhost:8001/current_transactions
```
![image](/images/current_transacs_after.PNG?raw=true)

