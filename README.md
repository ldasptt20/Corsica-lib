# Corsica Lib · Espace membre

Cette branche ajoute un serveur Django et un client Android de développement. La vitrine et la démonstration statiques restent des points d’entrée distincts. Le serveur privé ouvre directement l’espace membre sur `/`.

## Démarrer en local

Prérequis : Python 3.12. Depuis la racine du dépôt :

```sh
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
export SESSION_SECRET="$(python -c 'import secrets; print(secrets.token_urlsafe(64))')"
python manage.py migrate
python manage.py runserver 127.0.0.1:8000
```

Ouvrir http://127.0.0.1:8000/inscription/. Conserver le secret entre les redémarrages pour que les liens et les sessions restent valides. Les migrations créent une base SQLite dans le répertoire privé `.private/` (mode 0700). La base, les photos et les sessions sont exclues du dépôt. Pour cet essai sur une seule machine, utiliser un disque chiffré et un compte système dédié si des données réelles sont utilisées.

## Confirmation et majorité

Configurer côté serveur `SMTP_HOST`, `SMTP_PORT` (587 par défaut), `SMTP_USER`, `SMTP_PASSWORD`, `MAIL_FROM` pour les e-mails avec STARTTLS. Un échec de livraison laisse le compte en attente et permet un renvoi. La confirmation requiert le lien valable 24 heures et la connexion au même compte. Les mots de passe sont hachés avec Argon2id. Les limites de tentatives sont partagées dans la base. Le serveur utilise l’adresse de son pair réseau, sans faire confiance aux en-têtes IP transmis par le navigateur.

Pour un essai contractuel chez Yoti, définir `YOTI_API_KEY`, `YOTI_SDK_ID` et `APP_BASE_URL` (origine privée HTTPS acceptée par le fournisseur). L’API configurée est celle du service AVS. Sans clés, l’accès aux profils reste fermé. Le selfie utilise un seuil estimé de 25 ans, avec contrôle passif de présence. Le document est une alternative à partir de 18 ans. Le serveur n’enregistre pas les images de vérification. Une réponse serveur corrélée et positive est nécessaire. Vérifier les méthodes activées sur le compte fournisseur avant un essai réel. Le portail et les photos sont réservés au propriétaire à ce stade.

## Vérifications

```sh
python manage.py test
python manage.py makemigrations --check --dry-run
```

Les tests utilisent une base éphémère, une boîte mail en mémoire et des réponses Yoti contrôlées. Les services externes se valident séparément en environnement privé.

## Android de développement

Le projet `android/` affiche un accueil natif noir et fuchsia. Les boutons d’inscription et de connexion ouvrent le serveur privé dans le navigateur Android avec le protocole Custom Tabs. Le client partage ainsi la session du navigateur pour les confirmations et le retour de Yoti. Sa seule destination initiale est le serveur de développement sur le port 8000.

Avec Gradle 8.11.1, JDK 17 et Android SDK 35 installés, exécuter depuis la racine :

```sh
gradle -p android :app:assembleDebug
adb reverse tcp:8000 tcp:8000
adb install -r android/app/build/outputs/apk/debug/app-debug.apk
```

Le téléphone de test doit être connecté par USB avec le débogage activé et le serveur local démarré. L’essai de livraison sur téléphone, le parcours réel de caméra Yoti et la signature de distribution restent des étapes ultérieures.
