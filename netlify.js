// This is a config file to help Netlify detect this as a Vite project
export default {
  framework: 'vite',
  vite: {
    // Vite-specific options
    configFile: './vite.config.js'
  },
  // Explicitly disable Next.js
  nextjs: false,
  plugins: []
}
