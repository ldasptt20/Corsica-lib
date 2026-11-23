# Corsica Lib — Architecture Android web-app (plan privé)
Date : 2026-11-23
Statut : proposition technique, non déployée.

## Décision et périmètre
- Priorité exclusive : expérience mobile Android de type web-app, installable sur Xiaomi.
- Ne pas modifier, redéployer ni remplacer le site vitrine public sur `main`.
- Conserver `backup/corsica-lib-android-2026-11-23` et l'APK Java 0.3 comme points de restauration.
- Ne pas prétendre qu'une vraie infrastructure membre ou une vérification d'âge est déjà opérationnelle.
- Identité : noir profond / fuchsia, interface accessible et responsive, sans rubrique Événements.

## Schéma cible

```text
Xiaomi Android
  ├── PWA installable (premier canal de test recommandé)
  └── enveloppe Android TWA / Bubblewrap (étape ultérieure, si domaine HTTPS vérifié)
          │ HTTPS (authentification, CSRF / cookies sécurisés)
          ▼
  Frontend privé responsive (Vite + TypeScript + Vue 3)
          │ /api/...
          ▼
  API Django existante, étendue sous contrôle
          ├── PostgreSQL (comptes, profils, messages, autorisations)
          ├── Redis (limites / tâches / notifications au besoin)
          ├── médias privés avec autorisations par requête
          ├── email transactionnel
          └── vérification de majorité chez un fournisseur approuvé
```

Le backend Django actuel reste réutilisable. Les endpoints `/api/mobile/` sont un point de départ : définir des contrats d'API versionnés, une gestion explicite des erreurs, une validation des autorisations et des tests.

## Choix de l'enveloppe Android
1. D'abord PWA : manifest, icônes, service worker limité aux fichiers publics du frontend, aucun cache des messages, photos privées ni réponses d'authentification. Mode installation depuis Chrome Android.
2. Puis TWA : intégrer Bubblewrap quand l'application de préproduction a un domaine HTTPS et la vérification Digital Asset Links. Garder une stratégie de distribution indépendante tant que l'éligibilité Play Store n'est pas établie.
3. Ne pas garder par défaut une WebView arbitraire : authentification, gestion des liens et restrictions de sécurité s'en trouvent compliquées.
4. API et frontend ne sont pas une page du site vitrine : utiliser un domaine ou sous-domaine privé distinct. Aucune mise en ligne automatique.

## Modes
- `DEMO` : navigation locale avec personnages et conversations strictement fictifs, clairement étiquetés « démonstration ». Aucun compte ni vraie vérification, pas de données personnelles, pas de promesse de messagerie réelle.
- `PRIVATE_STAGING` : serveur HTTPS privé, accès de test, base dédiée, comptes de test uniquement, logs minimisés.
- `PRODUCTION` : désactivé tant que tous les contrôles ne sont pas satisfaits.
- Éviter que des données fictives puissent être envoyées à la vraie API.

## Navigation prévue
- Accueil / découverte : cartes de profils, filtre par ville et type de profil.
- Messages : liste des discussions, conversation avec pagination, état vide, blocage.
- Favoris : liste et gestion.
- Mon profil : édition, photos et confidentialité.
- Compte : vérification de majorité, gestion de session, sécurité, suppression.
- Premium : grille et avantages seulement en démonstration ; paiement désactivé.
- Aucun espace « Événements ».

## Sécurité et protection des personnes
- Bloquer l'accès aux vrais profils et médias avant vérification de majorité côté serveur ; choisir et tester réellement un fournisseur (Yoti/Didit : décision à stabiliser), avec preuve serveur, expiration et traitement des faux négatifs.
- Contrôles d'autorisation systématiques pour profil, conversation, favoris, albums et médias ; stockage des médias privé, URLs éphémères seulement après autorisation.
- Consentement explicite du propriétaire de l'album, révocation, traitement des contenus non consentis et procédure de signalement et retrait.
- Cookies Secure, HttpOnly, SameSite configurés ; CSRF pour requêtes à état ; CSP ; aucune clé API dans le frontend ; limites de débit et protections anti-spam.
- HTTPS obligatoire hors boucle locale de développement, secrets en environnement sécurisé.
- Sauvegardes chiffrées avec tests de restauration, droits RGPD (accès, suppression, rétention), registres minimisés, hébergement approprié.
- Revue juridique française et conditions du fournisseur avant ouverture ; règles Google Play sur rencontres, contenus sexuels et contenu utilisateur à évaluer selon les fonctions effectivement proposées. Ne pas présumer une approbation Play.

## Plan de migration sans toucher au site public
1. Conserver la sauvegarde et créer cette branche d'architecture.
2. Développer `mobile-web/` sur branche séparée. Maquettes interactives hors ligne d'abord.
3. Ajouter les tests du frontend (navigation, accessibilité, résolution Xiaomi) et la PWA, avec séparation claire mode démo / serveur privé.
4. Préparer une API de test avec PostgreSQL et données artificielles, ajouter les tests de sécurité / intégration.
5. Mettre à disposition une préproduction HTTPS privée, tester login et conformité 18+.
6. Produire l'enveloppe TWA seulement quand le domaine privé est vérifié ; tester l'installation et les liens sur Xiaomi.
7. Décision explicite ultérieure sur publication, paiements et distribution ; ne jamais fusionner automatiquement dans `main`.

## Validation avant de dire « fonctionnel »
- Installer sur Xiaomi et vérifier toutes les résolutions et le bouton Retour.
- Démarrage hors ligne du mode démo, sans exposition de données privées.
- Connexion aux services de staging, déconnexion, expiration de session, erreurs réseau.
- Parcours de majorité réel dans un environnement contractuellement autorisé.
- Tests d'accès croisé entre utilisateurs, blocage / signalement, suppression du compte.
- Build reproductible et artefact archivé.
