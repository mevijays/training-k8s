```
// First create .npmrc in your home directory (~/.npmrc)
// This sets up authentication for the private registry
@mevijay:registry=https://git.mevijay.dev/api/v4/projects/npm/
//git.mevijay.dev/api/v4/projects/npm/:_authToken="your-auth-token"
```
// package.json
```
{
  "name": "@mevijay/my-demo-package",
  "version": "1.0.0",
  "description": "A demo package using private npm registry",
  "main": "index.js",
  "scripts": {
    "test": "echo \"Error: no test specified\" && exit 1"
  },
  "keywords": ["demo", "npm", "package", "private"],
  "author": "Your Name",
  "license": "MIT",
  "publishConfig": {
    "registry": "https://git.mevijay.dev/api/v4/projects/npm/"
  }
}
```

// Create .npmrc in your project directory
```
@mevijay:registry=https://git.mevijay.dev/api/v4/projects/npm/
```

// index.js - Main package file (remains the same)
```
function greet(name) {
    return `Hello, ${name}! Welcome to my private demo package.`;
}

function add(a, b) {
    return a + b;
}

module.exports = {
    greet,
    add
};
```

// README.md
# @mevijay/my-demo-package

A private package hosted on git.mevijay.dev registry.

## Installation

First, authenticate with the private registry:

```bash
npm login --registry=https://git.mevijay.dev/api/v4/projects/npm/
```

Then install the package:

```bash
npm install @mevijay/my-demo-package
```

## Usage

```javascript
const demo = require('@mevijay/my-demo-package');

console.log(demo.greet('John')); // Hello, John! Welcome to my private demo package.
console.log(demo.add(5, 3));     // 8
```

// .gitignore
```
node_modules/
.DS_Store
*.log
.npmrc

```
