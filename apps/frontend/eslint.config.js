import js from '@eslint/js';
import boundaries from 'eslint-plugin-boundaries';
import jsxA11y from 'eslint-plugin-jsx-a11y';
import reactHooks from 'eslint-plugin-react-hooks';
import security from 'eslint-plugin-security';
import globals from 'globals';
import tseslint from 'typescript-eslint';

// Hexagonal layers; `interfaces` holds components, pages and routing.
const LAYERS = ['domain', 'application', 'interfaces', 'infrastructure'];

export default tseslint.config(
  { ignores: ['coverage/', 'dist/', 'node_modules/', 'playwright-report/', 'test-results/'] },
  js.configs.recommended,
  ...tseslint.configs.strictTypeChecked,
  jsxA11y.flatConfigs.recommended,
  security.configs.recommended,
  {
    languageOptions: {
      globals: { ...globals.browser },
      parserOptions: { projectService: true, tsconfigRootDir: import.meta.dirname },
    },
    plugins: { boundaries, 'react-hooks': reactHooks },
    rules: {
      ...reactHooks.configs.recommended.rules,
      '@typescript-eslint/no-explicit-any': 'error',
      'boundaries/dependencies': [
        'error',
        {
          default: 'disallow',
          policies: [
            {
              allow: { to: { element: { type: 'domain' } } },
              from: { element: { type: 'domain' } },
            },
            {
              allow: { to: { element: { types: { anyOf: ['application', 'domain'] } } } },
              from: { element: { type: 'application' } },
            },
            {
              allow: {
                to: { element: { types: { anyOf: ['application', 'domain', 'interfaces'] } } },
              },
              from: { element: { type: 'interfaces' } },
            },
            {
              allow: {
                to: { element: { types: { anyOf: ['application', 'domain', 'infrastructure'] } } },
              },
              from: { element: { type: 'infrastructure' } },
            },
          ],
        },
      ],
      'no-console': 'error',
    },
    settings: {
      'import/resolver': { typescript: { project: './tsconfig.json' } },
      'boundaries/elements': LAYERS.map((layer) => ({
        partialMatch: false,
        pattern: `src/${layer}/**`,
        type: layer,
      })),
    },
  },
  { files: ['**/*.js'], ...tseslint.configs.disableTypeChecked },
);
