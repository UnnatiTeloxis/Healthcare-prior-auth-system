# Custom Implementation Guides

Place custom FHIR Implementation Guide packages (.tgz files) in this directory.

## Usage

1. Place your custom IG package.tgz files here
2. Restart the Docker containers
3. The Inferno validator wrapper will load these IGs automatically

## Creating Custom IG Packages

Custom IG packages must conform to the [NPM Package Specification](https://confluence.hl7.org/display/FHIR/NPM+Package+Specification) and include a `.index.json` file.

## Example

```
igs/
├── my-custom-ig-1.0.0.tgz
└── another-ig-2.0.0.tgz
```
