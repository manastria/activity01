import { defineCollection, z } from 'astro:content';
import { docsSchema } from '@astrojs/starlight/schema';

const docs = defineCollection({
  type: 'content',
  schema: docsSchema({
    // Extend the default Starlight docs frontmatter schema
    extend: () => z.object({
      duration: z.string().optional(),     // e.g., "1h30"
      level: z.string().optional(),        // e.g., "BTS SIO 1"
      tags: z.array(z.string()).optional(),// e.g., ["docker", "réseau"]
      status: z.enum(['draft', 'ready', 'review']).default('draft').optional(),
    }),
  }),
});

export const collections = { docs };