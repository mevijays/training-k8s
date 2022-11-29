# Openshift 
To start with you can enable trial from here [Redhat openshift developer sandbox ](https://developers.redhat.com/developer-sandbox)
# Build
It would be easier to use ``oc new-build`` and then ``oc new-app`` if you really need to set this up as two steps for some reason. If you just want to setup the build and deployment in one go, just use ``oc new-app``.

For example, to setup build and deployment in one go use:
```
oc new-app --name myapp <repository-url>
```
To do it in two steps use:
```
oc new-build --name myapp <repository-url>
oc new-app myapp
```
