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
          label: 'Activités',
          autogenerate: { directory: 'activities', collapsed: false },
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
});