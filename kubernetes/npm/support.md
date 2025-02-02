Here are the steps to use this private registry setup:

Configure authentication:

bashCopynpm login --registry=https://git.mevijay.dev/api/v4/projects/npm/
# Enter your username and password when prompted

Create and set up your package:

bashCopymkdir my-demo-package
cd my-demo-package
npm init --scope=@mevijay

Create your auth token (replace username/password with your credentials):

bashCopyecho -n 'username:password' | base64
# Use this output as your auth token in .npmrc

Test the package locally:

bashCopynode
> const demo = require('./index.js')
> demo.greet('Test')

Publish to private registry:

bashCopynpm publish
To install and use the package in other projects:

Add registry configuration to the project:

bashCopyecho "@mevijay:registry=https://git.mevijay.dev/api/v4/projects/npm/" > .npmrc

Install the package:

bashCopynpm install @mevijay/my-demo-package
Key changes from the public version:

Added scope (@mevijay) to package name
Configured private registry URL
Added authentication setup
Updated documentation for private registry usage
Added publishConfig in package.json
Created separate .npmrc files for global and project-specific settings

Would you like me to explain any of these configurations in more detail?
