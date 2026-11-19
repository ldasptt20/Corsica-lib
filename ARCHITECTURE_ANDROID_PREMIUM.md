# Corsica Lib — architecture de distribution et d'accès (décision produit, 19 novembre 2026)

## Décision validée
Corsica Lib cible les adultes résidant en Corse ou en visite. Conserver l'identité visuelle noire et fuchsia. Proposer deux services distincts, sans prétendre que la plateforme adulte est publiée ou approuvée par Google Play.

### 1. Application Android native distribuée via Google Play
- Fonction centrale : rencontre entre adultes, profils, filtres géographiques corses, favoris et messagerie.
- Photos de profil et autres contenus visibles dans l'application : uniquement ceux autorisés par les règles Google Play, soumis à modération.
- Inscription, connexion et vérification de majorité avant l'accès aux fonctions réservées aux adultes.
- Blocage et signalement des comptes et contenus, suppression du compte et de ses données, traitement des demandes RGPD.
- Aucun affichage de médias explicites, aucune galerie adulte explicite intégrée ou chargée à distance dans l'application, y compris pour les abonnés.
- Ne pas concevoir de redirection visant à contourner les règles Google Play.
- Publication conditionnée à une revue des politiques Google Play en vigueur.

### 2. Plateforme adulte indépendante (hors Google Play)
- Service distinct, accessible seulement aux adultes vérifiés ; conformité juridique et contrôle de majorité adaptés à la France, à confirmer avant ouverture.
- Albums privés (photos et vidéos) : publication et accès subordonnés au consentement des personnes représentées et aux droits sur les médias.
- Contenus explicitement consentis entre adultes uniquement ; interdiction des mineurs et des contenus non consentis ; signalement, retrait rapide, traçabilité et modération.
- Contrôles d'autorisation à chaque requête sur les médias (pas de simple URL publique) ; stockage privé, chiffrement, rétention et suppression maîtrisées.
- Évaluer séparément l'hébergeur, les conditions d'utilisation, la protection des données et le prestataire de paiement acceptant cette activité.
- Ne pas supposer que Google Play Billing peut facturer des services consommés exclusivement sur une plateforme externe.

### 3. Offres commerciales envisagées
- Inscription gratuite.
- VIP mensuel : 9,99 EUR ; 3 mois : 24,99 EUR ; annuel : 89,99 EUR.
- Même grille pour résidents et touristes, sans offre touristique.
- Avantages, périmètre de facturation et droits d'accès à définir précisément par service avant d'intégrer la facturation.
- Ne pas activer les abonnements tant que le parcours d'achat, d'annulation et de restauration n'est pas testé.

## Situation technique vérifiée
- Branche de travail : `feature/android-build-validation`.
- Projet Android natif : `android/app`, Gradle 8.11.1 dans les workflows, Android Gradle Plugin 8.9.2.
- API Django : `members/mobile.py` avec connexion, profils, annuaire, favoris et messages.
- `android/app/build.gradle` utilise encore une origine de développement locale par défaut. La publication nécessite une URL de serveur HTTPS opérationnelle.
- Les dernières exécutions GitHub Actions examinées se terminent par `startup_failure` avec zéro job. Aucune compilation APK/AAB réussie n'a été démontrée.

## Étapes de livraison à valider
1. Diagnostiquer la cause de `startup_failure` dans GitHub Actions et obtenir une exécution de build réelle avec journaux.
2. Corriger les erreurs Gradle/Android éventuelles, produire et installer un APK de test sur téléphone.
3. Configurer le serveur HTTPS, sécuriser les sessions et tester tous les parcours de l'application.
4. Construire et tester les mécanismes de modération et de vérification d'âge.
5. Définir les droits VIP et le paiement conformes au canal de distribution ; tester tous les renouvellements et annulations.
6. Concevoir et développer séparément la plateforme adulte, puis réaliser une revue juridique, RGPD et fournisseur.
7. Générer un AAB Android signé et soumettre la seule application conforme à Google Play Console.

**Ce document est une décision d'architecture et une feuille de route ; il ne représente ni une fonctionnalité déjà implémentée ni une certification de conformité.**
