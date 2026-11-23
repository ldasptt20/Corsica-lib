# Corsica Lib — Design approuvé (référence figée)
Date de validation : 23 novembre 2026
Décision : l'utilisateur approuve et souhaite CONSERVER la maquette à quatre écrans présentée dans la conversation, sans modification esthétique non sollicitée.

## Référence visuelle canonique
Image originale « aperçu Corsica Lib PWA + TWA — 4 écrans », enregistrée dans la bibliothèque de fichiers du projet sous :
`/Corsica Lib/Design approuve/CorsicaLib-maquette-4-ecrans-2026-11-23.png`
La référence graphique exacte se trouve dans cette image. Ne pas substituer un autre visuel générique.

## Identité
- Nom : Corsica Lib
- Signature sur la maquette : « Rencontres libertines en Corse »
- Palette dominante : noir presque pur, panneaux anthracite, rose fuchsia vif, texte blanc, touches de gris et badges verts pour présence en ligne.
- Logo : silhouette de la Corse avec cœur rose.
- Direction esthétique : haut de gamme, contrastée, contemporaine, angles arrondis, cartes avec photographies et dégradés, typographie lisible.
- Navigation persistante en bas : Accueil, Rechercher, Messages, Favoris, Profil. Onglet actif en fuchsia.
- Les photographies et personnages de la maquette sont fictifs. Ne pas les considérer comme des utilisateurs réels.

## Écrans canonisés
1. **Accueil / Découverte** : barre de marque et notification, onglets Découvrir / En ligne / À proximité, grille de profils, âge et ville, indication en ligne, icônes favoris, filtre en bas.
2. **Profil détaillé** : photo principale plein écran, prénom, âge, distance/ville, tags et disponibilité, zone « À propos », centres d'intérêt, boutons favoris et message.
3. **Messagerie** : onglets Conversations / Demandes, recherche de conversations, lignes avatar/pseudo/extrait/heure/non-lus, pied de navigation.
4. **Mon espace** : avatar du membre, accès à Mon profil, Mes favoris, Mes visites, Mon abonnement Premium, Paramètres & confidentialité, Aide & contact, Déconnexion.

## Consignes pour reprise
- Conserver ce design comme **référence approuvée** lors du développement de la web-app Android.
- Développer d'abord la démo hors ligne avec données fictives, puis raccorder à une API privée sécurisée.
- La cible de distribution est PWA installable sur Xiaomi, puis éventuellement enveloppe TWA vérifiée.
- Interface 18+, vérification de majorité sur serveur réel avant données privées ; confidentialité, modération et consentement requis.
- Pas d'espace Événements.
- Ne pas changer ni publier le site vitrine : la branche `main` reste inchangée.
- Conserver les branches `backup/corsica-lib-android-2026-11-23` et `architecture/webapp-android-private`.
- L'approbation de la maquette ne vaut ni déploiement ni preuve que les écrans sont déjà développés.

## Étape suivante à la reprise
Créer les écrans Vue 3/TypeScript correspondants en mode démo, avec navigation cohérente et responsive et une PWA installable. Tester sur Xiaomi avant raccordement au serveur.
