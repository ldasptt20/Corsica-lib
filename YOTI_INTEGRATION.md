# Inscription sécurisée Corsica Lib — intégration Yoti

## Branche de développement
Le serveur membre, ses tests et les paramètres de configuration sont décrits dans [le README](README.md). Le parcours réel avec un compte Yoti reste à valider.

## État de la vitrine publique
Le site actuel est une démonstration statique. **L'inscription réelle reste fermée** tant qu'un backend sécurisé, une base de données, un contrat Yoti et des clés de production ne sont pas configurés.

## Parcours obligatoire
1. Le visiteur choisit « Créer un compte », renseigne un email et un mot de passe uniquement dans la future application backend (pas dans la page statique).
2. Le serveur crée un compte **pending_age_verification** non autorisé à accéder aux fonctions adultes. Email à confirmer, mots de passe hachés avec Argon2id, protection contre les tentatives répétées, cookies de session Secure/HttpOnly/SameSite.
3. Le backend crée une **session unique** Yoti Age Verification Service (AVS), configurée pour la **Facial Age Estimation par selfie en direct**, avec contrôle anti-usurpation (liveness) et seuil de confiance/marge de sécurité recommandés par Yoti. Le service doit vérifier la majorité (18+), pas prétendre identifier la personne. Prévoir un contrôle alternatif et un recours lorsque l'estimation échoue ou reste incertaine. Le SDK ID et la clé API ne doivent **jamais** figurer dans le JavaScript public.
4. L'utilisateur est redirigé vers l'interface Yoti hébergée et prend un selfie en direct avec sa caméra ; **Corsica Lib ne collecte ni ne stocke ce selfie**. Prévoir les méthodes compatibles avec les exigences françaises applicables, notamment si une vérification en double anonymat est requise.
5. Après le retour, le **serveur** interroge Yoti via l'API de résultats et vérifie l'authenticité, le statut final, le seuil d'âge et la correspondance avec la session initiée et le compte en attente. Ne jamais se fier à une simple query string de succès.
6. Si vérifié majeur : le serveur marque le compte comme autorisé et crée une session authentifiée. Sinon : accès refusé. Prévoir expiration, annulation, répétition et assistance.
7. Vérifier l'autorisation **sur chaque route API** (profils, recherche, messages, salons, albums), pas simplement sur l'interface.
8. Stocker le strict minimum : identifiant interne, statut majeur vérifié, date, référence de contrôle utile ; ne pas stocker selfies ou pièces d'identité chez Corsica Lib. Définir durée de conservation, information RGPD, consentement/modération, politique de confidentialité et sécurité des médias.
9. Prévoir suppression de compte, signalement, blocage, modération, protection des albums et photos. Tester l'ensemble avant l'ouverture.

## Choix produit confirmé — 18 novembre 2026
La méthode principale demandée est **Yoti avec selfie** (estimation faciale de l'âge), sans téléchargement de photo dans Corsica Lib. L'intégration réelle n'est pas encore activée et ne peut pas l'être sur une page purement statique. Le retour de Yoti doit être vérifié côté serveur ; l'utilisateur ne doit pas accéder aux fonctions adultes sur simple clic.

## Configuration envisagée pour un hébergement ultérieur
- `YOTI_API_KEY` : secret, uniquement variable d'environnement serveur.
- `YOTI_SDK_ID` : identifiant Yoti AVS.
- `APP_BASE_URL` : adresse publique confirmée.
- `SESSION_SECRET`, `DATABASE_URL` : secrets distincts. Aucun secret dans GitHub.
- HTTPS, base de données persistante, sauvegardes, journalisation minimale sans données d'identité.

## Documentation officielle
- https://developers.yoti.com/age-verification/quick-start
- https://developers.yoti.com/age-verification/methods
- https://developers.yoti.com/age-verification/results
- https://www.yoti.com/privacy/age-verification/fr/

## À valider avant mise en production
- Compte professionnel Yoti approuvé et fonctionnalités contractuelles nécessaires.
- Choix d'une méthode de contrôle conforme en France selon les contenus effectivement publiés (vérification indépendante, double anonymat si requis).
- Backend opérationnel, base de données, gestion des comptes, emails, accès, preuves de test.
- Aucun accès aux contenus adultes en cas de vérification absente, indéterminée ou échouée.
