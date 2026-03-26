import { defineConfig } from "astro/config";
import starlight from "@astrojs/starlight";
import icon from "astro-icon";

export default defineConfig({
  // Configuration au premier niveau
  integrations: [
    starlight({
      title: "Manastria · Cours",
      favicon: '/favicon.svg',
      locales: { root: { label: "Français", lang: "fr" } },
      sidebar: [
        { label: "Accueil", link: "/" },
        {
          label: "CRASH Test",
          collapsed: true,
          autogenerate: {
            directory: "activities/crashtest",
            collapsed: false },
        },
        {
          label: "HaProxy",
          collapsed: true,
          autogenerate: {
            directory: "activities/activity-haproxy",
            collapsed: false },
        },
        // Ajout manuel de la catégorie SNS
        {
          label: "SNS", // Le nom de la catégorie dans le menu
          items: [
            { label: "Reset", link: "activities/sns/reset" },
            { label: "Configuration de base", link: "activities/sns/init" },
            {
              label: "Modèles pare-feu et NAT",
              link: "activities/sns/doc-regles",
            },
            {
              label: "NAT sortant SNAT",
              link: "activities/sns/nat-sortant-snat",
            },
            {
              label: "NAT entrant DNAT",
              link: "activities/sns/nat-entrant-dnat",
            },
            {
              label: "Configurer interface réseau CLI",
              link: "activities/sns/sns-configuration-interface-reseau-cli",
            },
          ],
        },
        {
          label: "Outils",
          items: [
            { label: "Déploiement clé SSH", link: "/outils/ssh-key-deployer" },
            { label: "Mémo", link: "/memo" },
          ],
        },
        {
          label: "VPN",
          collapsed: true,
          autogenerate: { directory: "activities/sns-vpn", collapsed: false },
        },
        {
          label: "Fiches",
          link: "fiches",
        },
      ],
      tableOfContents: {
        heading: "Sommaire",
        minHeadingLevel: 2,
        maxHeadingLevel: 4,
      },
      customCss: ['./src/styles/custom.css'],
    }),
    icon(),
  ],
  vite: {
    server: {
      allowedHosts: ["n110-prof.local"],
    },
  },
  site: "https://manastria.github.io",
  base: "/activity01/",
  trailingSlash: "ignore",
});
