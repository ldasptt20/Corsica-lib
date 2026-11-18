# Corsica Lib — feuille de route site + Android (18 novembre 2026)

## Objectif
Un service de rencontres pour adultes en Corse, inspiré des fonctions générales des sites de rencontres, avec identité propre. Même compte et mêmes droits pour le site et la version Android. Design noir et rose fuchsia. Aucune rubrique « Événements ».

## État vérifié
- `index.html` : page publique de présentation.
- `demo.html` : maquette navigable. L'inscription et les paiements ne sont pas fonctionnels.
- PWA : manifest et service worker déjà ajoutés au projet.
- `YOTI_INTEGRATION.md` : exigences d'intégration Yoti documentées.
- Aucune API ou base utilisateurs fonctionnelle identifiée dans les fichiers inspectés. Ne pas annoncer une ouverture des inscriptions.

## Architecture cible
- Frontend responsive Web/PWA pour Android, partageant les mêmes services API et comptes. Application Android native ou enveloppe Android à étudier après validation des politiques de distribution.
- Backend HTTPS : authentification, confirmation e-mail, mots de passe hachés Argon2id, sessions sécurisées, limitation de débit, journalisation minimale, contrôles d'accès systématiques.
- Base PostgreSQL : comptes, profils, consentements, vérifications d'âge (statut seulement), conversations, messages, demandes d'accès aux albums, abonnements, signalements, blocages.
- Fichiers médias dans stockage privé avec URLs temporaires et droits vérifiés côté serveur, pas dans GitHub ni en URLs publiques.
- Vérification Yoti Age Verification Service : session créée sur le serveur, selfie sur interface Yoti, vérification du résultat côté serveur, état mineur/inconnu = accès bloqué ; recours alternatif en cas d'incertitude. Les clés Yoti demeurent uniquement dans Render.
- Outils de modération : signaler, bloquer, retirer les médias, traiter les abus et les atteintes au consentement.

## Ordre de réalisation et critères de validation
1. **Infrastructure sécurisée** : backend Render, base PostgreSQL, secrets d'environnement, migrations, tests et environnement de préproduction distinct. Jamais de secrets GitHub.
2. **Inscription 18+** : création de compte en attente, confirmation e-mail, session Yoti selfie, résultat authentifié et accès fermé par défaut. Tests de refus et d'expiration obligatoires.
3. **Profils et recherche** : célibataires / couples, recherche par ville corse, confidentialité par défaut et consentement de chaque personne représentée.
4. **Messagerie gratuite** : accès entre membres vérifiés, blocage, signalement, anti-spam et modération.
5. **Albums privés** : autorisation explicite de leur propriétaire, révocation possible ; Premium ne contourne jamais cette autorisation.
6. **Salons et VIP** : salon général et salon Premium, mesures de modération.
7. **Paiements** : offres envisagées 3,99 € / 3 jours et 9,99 € / 1 mois, pas de renouvellement obligatoire, validation juridique/PSP et webhooks serveur.
8. **Android** : PWA installable d'abord, puis option de distribution adaptée aux règles applicables. Google Play limite les contenus sexuels et les fonctionnalités payantes encourageant le partage explicite : publication sur Play non garantie.
9. **Avant ouverture** : RGPD (information, droits, conservation, suppression), conformité française de la vérification d'âge selon le contenu réellement autorisé, CGU, modération, tests de sécurité, conformité des paiements, sauvegardes, politique de prévention et protection des mineurs.

## Blocages externes à résoudre pour la mise en production
- Compte professionnel Yoti, service contractuel activé, identifiants et tarifs.
- Choix et configuration d'envoi d'e-mails transactionnels.
- Responsable légal du site et documents RGPD/CGU ; validation de la conformité des contenus.
- Prestataire de paiement acceptant les activités envisagées et règles de facturation.
- Stratégie de distribution Android (Google Play après conformité ou installation directe de la PWA).

Cette feuille de route est une spécification, pas une confirmation de fonctionnalités déjà implémentées. Ne jamais présenter la maquette comme une vraie vérification Yoti.