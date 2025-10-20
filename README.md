# WhaleSounds

WhaleSounds est une application libre, gratuite et ultra-intuitive pour l’écoute de sons marins.

C'est avant tout un logiciel pédagogique utilisé lors d’événements. Bien que son nom porte sur les cétacés, on peut jouer n'importe quels sons.

Le spectrogramme y sert d’exemple simple pour montrer comment les chercheurs en acoustique peuvent étudier un son. Et puis, c’est aussi fascinant à regarder !

Les fichiers audios et les images ne sont pas fournies dans ce repo !

## Fonctionnalités principales
- **Mode simple** : galerie d'images des animaux (ou autre), écoute rapide des sons associés.
- **Mode complet** : visualisation avancée (spectrogramme, waveform).

## Installation

1. **Cloner le dépôt**

```bash
git clone https://github.com/votre-utilisateur/WhaleSounds.git
cd WhaleSounds
```

2. **Installer les dépendances**

Assurez-vous d'avoir Python 3.9+ et pip installés.

```bash
pip install -r requirements.txt
```

> Les dépendances principales :
> - PySide6
> - PyYAML
> - pyqtgraph
> - soundfile
> - qt-material (optionnel pour le thème)

3. **Lancer l'application**

```bash
python main.py
```

## Structure du projet

- `main.py` : point d'entrée, gestion des onglets et de la navigation.
- `home_page.py` : page d'accueil avec cards de sélection.
- `simple_viewer.py` : mode galerie simple.
- `whalemainwindow.py` : mode complet (exploration avancée).

## Personnalisation
- Ajoutez un dossier `data` à la racine du projet. Ajoutez vos propres images/sons dans `data/` et référencez-les dans `data/whale_data.yml`.

### Personnalisation de whale_data.yml
```yaml
Genre 1:
    Espèce 1:
        sons: 
        - "path fichier 1"
        - ...
        image: "path image"
        credits: 'Credit image, son ou autre info'
    Espèce 2:
        sons: 
        - "path fichier 1"
        - ...
        image: "path image"
        credits: 'Credit image, son ou autre info'
Genre 2:
    Espèce 1:
        sons: 
        - "path fichier 1"
        - ...
        image: "path image"
        credits: 'Credit image, son ou autre info'
```

Genre 1 et Genre 2 deviendront des boutons de filtrage des espèces référencées dans le fichier.

**Projet pédagogique et exploratoire.**
