import pluginVue from 'eslint-plugin-vue'
import vueTsEslintConfig from '@vue/eslint-config-typescript'
import pluginVitest from '@vitest/eslint-plugin'
import pluginCypress from 'eslint-plugin-cypress/flat'
import skipFormatting from '@vue/eslint-config-prettier/skip-formatting'

export default [
  {
    name: 'app/files-to-lint',
    files: ['**/*.{ts,mts,tsx,vue}'],
  },

  {
    name: 'app/files-to-ignore',
    ignores: ['**/dist/**', '**/dist-ssr/**', '**/coverage/**'],
  },

  // Vue plugin configuration (for Composition API support)
  {
    ...pluginVue.configs['flat/essential'],
    rules: {
      // Ensure Composition API syntax works correctly
      'vue/valid-v-slot': 'off', // If this causes issues with scoped slots
      'vue/no-v-model-argument': 'off', // Disable if needed (for customization)
      'vue/multi-word-component-names': 'off', // Can be useful to turn off for simplicity in some cases
      'vue/script-setup-uses-vars': 'error', // Ensure `script setup` variables are treated properly
    },
  },

  // TypeScript configuration for Vue
  {
    ...vueTsEslintConfig(),
    rules: {
      // TypeScript-specific rules to allow Composition API to work smoothly
      'no-unused-vars': ['warn', { argsIgnorePattern: '^_' }], // Ignore unused vars with leading underscores (common in Composition API)
      '@typescript-eslint/no-unused-vars': ['warn', { argsIgnorePattern: '^_' }],
    },
  },

  // Vitest for testing
  {
    ...pluginVitest.configs.recommended,
    files: ['src/**/__tests__/*'],
  },

  // Cypress for E2E testing
  {
    ...pluginCypress.configs.recommended,
    files: [
      'cypress/e2e/**/*.{cy,spec}.{js,ts,jsx,tsx}',
      'cypress/support/**/*.{js,ts,jsx,tsx}',
    ],
  },

  // Prettier skip formatting (if needed)
  skipFormatting,
]
