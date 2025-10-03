# Changelog

All notable changes to Interview Corvus will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Installation guide (INSTALLATION.md)
- Changelog documentation (CHANGELOG.md)

## [0.2.3] - 2024-01-XX

### Changed
- Refactored chunk processing functionality

### Fixed
- Code improvements and optimizations

## [0.2.2] - 2024-01-XX

### Added
- Multi-language support for coding solutions (Python, Java, JavaScript, C++, C#, Go, Rust, Ruby)
- Screenshot-based problem solving with OCR
- Time and space complexity analysis
- Edge case handling and identification
- Solution optimization feature
- Global hotkey system for keyboard controls

### Changed
- Improved UI with customizable themes (Light/Dark)
- Enhanced prompt template system
- Better API key management with secure keychain storage

### Fixed
- Platform-specific permission handling
- Hotkey conflicts resolution
- Screen sharing invisibility improvements

## [0.2.1] - 2024-01-XX

### Added
- Cross-platform support (macOS, Windows, Linux)
- PyQt6-based user interface
- Anthropic Claude API support
- OpenAI GPT-4/GPT-4o support
- Customizable hotkeys for different platforms
- Window positioning controls
- Settings persistence

### Changed
- Migrated to Poetry for dependency management
- Improved build system with platform-specific packaging

### Fixed
- macOS Gatekeeper compatibility
- Windows permission issues
- Linux desktop integration

## [0.2.0] - 2024-01-XX

### Added
- Initial public release
- AI-powered coding assistant functionality
- Invisible mode for screen sharing
- Screenshot capture capability
- Real-time code solution generation
- Customizable prompt templates
- Secure API key storage using system keychain

### Changed
- Complete rewrite based on interview-coder project
- Modern Python architecture with Pydantic settings
- LlamaIndex integration for LLM interactions

### Security
- Implemented secure API key storage with keyring library
- Added platform-specific security permissions

## [0.1.0] - 2024-01-XX

### Added
- Initial development version
- Basic UI framework
- Core LLM integration
- Screenshot functionality
- Configuration system

---

## Release Types

### Added
New features and functionality

### Changed
Changes to existing functionality

### Deprecated
Features that will be removed in upcoming releases

### Removed
Features that have been removed

### Fixed
Bug fixes and error corrections

### Security
Security-related changes and vulnerability fixes

---

## Version History Links

- [0.2.3]: https://github.com/afaneor/interview-corvus/releases/tag/v0.2.3
- [0.2.2]: https://github.com/afaneor/interview-corvus/releases/tag/v0.2.2
- [0.2.1]: https://github.com/afaneor/interview-corvus/releases/tag/v0.2.1
- [0.2.0]: https://github.com/afaneor/interview-corvus/releases/tag/v0.2.0
- [0.1.0]: https://github.com/afaneor/interview-corvus/releases/tag/v0.1.0

---

## Contributing to the Changelog

When contributing to this project, please update this changelog with your changes in the [Unreleased] section. Include:

- A clear description of the change
- The type of change (Added, Changed, Fixed, etc.)
- Any relevant issue or PR numbers

Example:
```markdown
### Added
- New feature description (#123)
```
