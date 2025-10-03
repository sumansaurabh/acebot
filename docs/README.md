# Interview Corvus Documentation

This directory contains the Docusaurus documentation for Interview Corvus.

## Quick Start

### Development Mode

Run the documentation site locally with hot-reload:

```bash
cd interview-corvus-docs
npm start
```

The site will open at `http://localhost:3000`

### Build for Production

Build static files for deployment:

```bash
cd interview-corvus-docs
npm run build
```

Static files will be generated in the `build/` directory.

### Serve Built Site

Test the production build locally:

```bash
cd interview-corvus-docs
npm run serve
```

## Documentation Structure

```
docs/
├── interview-corvus-docs/     # Docusaurus project
│   ├── docs/                  # Documentation content
│   │   ├── intro.md           # Introduction
│   │   ├── installation.md    # Installation guide
│   │   ├── usage/             # Usage guides
│   │   │   ├── getting-started.md
│   │   │   └── advanced-features.md
│   │   ├── customization/     # Customization docs
│   │   │   ├── overview.md
│   │   │   └── hotkeys.md
│   │   └── api/               # API documentation
│   │       └── overview.md
│   ├── src/                   # React components and pages
│   ├── static/                # Static assets
│   ├── docusaurus.config.ts   # Docusaurus configuration
│   └── sidebars.ts            # Sidebar configuration
└── README.md                  # This file
```

## Adding New Documentation

1. Create a new `.md` file in the appropriate directory under `docs/`
2. Add frontmatter at the top:
   ```md
   ---
   sidebar_position: 1
   ---

   # Your Page Title
   ```
3. The sidebar will automatically update based on the file structure

## Configuration

### Site Configuration

Edit `docusaurus.config.ts` to modify:
- Site title and tagline
- Navigation bar
- Footer
- Theme settings
- Deployment settings

### Sidebar

The sidebar is auto-generated from the `docs/` folder structure. To customize it manually, edit `sidebars.ts`.

## Available Commands

```bash
# Start development server
npm start

# Build for production
npm run build

# Serve production build
npm run serve

# Clear cache
npm run clear

# Deploy to GitHub Pages (if configured)
npm run deploy
```

## Documentation Features

- 📝 **Markdown support** - Write docs in Markdown
- 🔍 **Search** - Built-in search functionality
- 🌓 **Dark mode** - Automatic dark/light theme
- 📱 **Mobile responsive** - Works on all devices
- 🔗 **Versioning** - Support for multiple versions
- 🌐 **i18n** - Internationalization support

## Contributing

When adding or updating documentation:

1. Follow the existing structure and style
2. Use clear, concise language
3. Include code examples where appropriate
4. Add links to related pages
5. Test the build before committing

## Resources

- [Docusaurus Documentation](https://docusaurus.io/docs)
- [Markdown Guide](https://www.markdownguide.org/)
- [Interview Corvus Repository](https://github.com/afaneor/interview-corvus)
