import js from '@eslint/js';
import pluginReact from 'eslint-plugin-react';

export default [
  js.configs.recommended,
  {
    plugins: {
      react: pluginReact,
    },
    settings: {
      react: {
        version: 'detect',
      },
    },
    rules: {
      'no-cond-assign': ['error', 'always'],
      'indent': ['error', 2],
      'linebreak-style': ['error', 'unix'],
      'quotes': ['error', 'single'],
      'no-unused-vars': 'off',
      'semi': ['error', 'always'],
      'react/jsx-uses-react': 'error',
      'react/jsx-uses-vars': 'error',
    },
  },
];
