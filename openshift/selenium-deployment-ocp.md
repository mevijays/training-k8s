# Selenium Grid installation on Openshift-4


1- Deploy the HUB and expose the service
```
oc new-app --name sl-hub selenium/hub:latest
oc expose service/slnode-firefox
```

2- Deploy the chrome node

```
oc new-app --name slnode-chrome -e SE_EVENT_BUS_HOST=sl-hub -e SE_EVENT_BUS_PUBLISH_PORT=4442 -e SE_EVENT_BUS_SUBSCRIBE_PORT=4443 selenium/node-chrome:latest

```

Optional to deploy edge and firefox node as well

```
oc new-app --name slnode-firefox -e SE_EVENT_BUS_HOST=sl-hub -e SE_EVENT_BUS_PUBLISH_PORT=4442 -e SE_EVENT_BUS_SUBSCRIBE_PORT=4443 selenium/node-firefox:latest


oc new-app --name slnode-edge -e SE_EVENT_BUS_HOST=sl-hub -e SE_EVENT_BUS_PUBLISH_PORT=4442 -e SE_EVENT_BUS_SUBSCRIBE_PORT=4443 selenium/node-edge:latest

```
