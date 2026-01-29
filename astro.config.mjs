import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';

// 1) If deploying to GitHub Pages under a project repo, set `site` + `base`.
//    Example:
//    site: 'https://<user>.github.io/<repo>/',
//    base: '/<repo>/',
// 2) For a root domain or Infomaniak hosting, you can omit `base` and set `site` to your full URL.
export default defineConfig({
  // site: 'https://example.com/',
  // base: '/my-repo/', // only for GitHub project pages
  integrations: [
    starlight({
      title: 'Activités SISR',
      locales: { root: { label: 'Français', lang: 'fr' } },
      sidebar: [
        { label: 'Accueil', link: '/' },
        {
          label: 'Activités',
          // Auto-generate the group from files under src/content/docs/activities
          autogenerate: { directory: 'activities', collapsed: false },
        },
      ],
      tableOfContents: {
        heading: 'Sommaire',
        // Include all headings from the content files
        // include: ['h1', 'h2', 'h3'],
        minHeadingLevel: 2,
        maxHeadingLevel: 4,
      },
      // Add your analytics/scripts if needed using the `head` option.
    }),
  ],
});