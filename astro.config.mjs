import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';

export default defineConfig({
  // Configuration au premier niveau
  integrations: [
    starlight({
      title: 'Activités SISR',
      locales: { root: { label: 'Français', lang: 'fr' } },
      sidebar: [
        { label: 'Accueil', link: '/' },
        {
          label: 'CRASH Test',
          autogenerate: { directory: 'activities/crashtest', collapsed: true },
        },
        // Ajout manuel de la catégorie SNS
        {
          label: 'SNS', // Le nom de la catégorie dans le menu
          items: [
            { label: 'Reset', link: 'activities/sns/reset' },
            { label: 'Configuration de base', link: 'activities/sns/init' },
            
          ],
        },
      ],
      tableOfContents: {
        heading: 'Sommaire',
        minHeadingLevel: 2,
        maxHeadingLevel: 4,
      },
    }),
  ],
  // Le bloc vite doit être ICI, après la fermeture du tableau integrations
  vite: {
    server: {
      allowedHosts: ['n110-prof.local'],
    }
  },
  site: 'https://manastria.github.io/activity01/',
  base: '/activity01/'
});