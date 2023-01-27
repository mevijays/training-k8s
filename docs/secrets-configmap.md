# Secrets and Configmaps
## Secrets

Secrets are a Kubernetes object intended for storing a small amount of sensitive data.  It is worth noting that Secrets are stored base64-encoded within Kubernetes, so they are not wildly secure.  Make sure to have appropriate [Role-base access controls](https://kubernetes.io/docs/reference/access-authn-authz/rbac/) (or RBAC) to protect access to secrets. Even so, extremely sensitive secret data should probably be stored using something like [HashiCorp Vault](https://www.vaultproject.io/).  For the root password of a MariaDB database, however, they are just fine.


### Creating a Secret manually

To create the Secret containing the `MYSQL_ROOT_PASSWORD`, we need to first pick a password, and convert it to base64:

```
# The root password will be "KubernetesRocks!"
$ echo -n 'KubernetesRocks!' | base64
S3ViZXJuZXRlc1JvY2tzIQ==
```

Make a note of the encoded string.  We need it to create the YAML file for the Secret:

```
apiVersion: v1
kind: Secret
metadata:
  name: mariadb-root-password
type: Opaque
data:
  password: S3ViZXJuZXRlc1JvY2tzIQ==
```

Save that file as `mysql-secret.yaml` and create the secret in Kubernetes with the `kubectl apply` command:

```
$ kubectl apply -f mysql-secret.yaml
secret/mariadb-root-password created
```


### View the newly created Secret

Now that the secret is created, use `kubectl describe` to see it.

```
$ kubectl describe secret mariadb-root-password
Name:         mariadb-root-password
Namespace:    secrets-and-configmaps
Labels:       <none>
Annotations:
Type:         Opaque

Data
====
password:  16 bytes
```

Note the `Data` field contains the key we set in the YAML: `password`.  The value assigned to that key is the password we created, but it is not shown in the output.  Instead, the size of the value is shown in its place - in this case 16 bytes.

The `kubectl edit secret <secretname>` command can also be used to view and edit the secret.  Editing the secret we created shows something like:

```
# Please edit the object below. Lines beginning with a '#' will be ignored,
# and an empty file will abort the edit. If an error occurs while saving this file will be
# reopened with the relevant failures.
#
apiVersion: v1
data:
  password: S3ViZXJuZXRlc1JvY2tzIQ==
kind: Secret
metadata:
  annotations:
    kubectl.kubernetes.io/last-applied-configuration: |
      {"apiVersion":"v1","data":{"password":"S3ViZXJuZXRlc1JvY2tzIQ=="},"kind":"Secret","metadata":{"annotations":{},"name":"mariadb-root-password","namespace":"secrets-and-configmaps"},"type":"Opaque"}
  creationTimestamp: 2019-05-29T12:06:09Z
  name: mariadb-root-password
  namespace: secrets-and-configmaps
  resourceVersion: "85154772"
  selfLink: /api/v1/namespaces/secrets-and-configmaps/secrets/mariadb-root-password
  uid: 2542dadb-820a-11e9-ae24-005056a1db05
type: Opaque
```

Again, the `data` field with the `password` key is visible, and this time the base64-encoded secret.


### Decode the Secret

Let's say we need to view the secret in plain text. For example, we can verify that the secret was created with the correct content by decoding it.

It is easy to decode the secret by extracting the value and piping it to base64.  In this case we will use the output format `-o jsonpath=<path>` to extract only the secret value using a JSONPath template.

```
# Returns the base64 encoded secret string
$ kubectl get secret mariadb-root-password -o jsonpath='{.data.password}'
S3ViZXJuZXRlc1JvY2tzIQ==

# Pipe it to `base64 --decode -` to decode:
$ kubectl get secret mariadb-root-password -o jsonpath='{.data.password}' | base64 --decode -
KubernetesRocks!
```

### Another way to create Secrets

It is also possible to create Secrets directly using the `kubectl create secret` command.  The MariaDB image also allows for setting up a regular database user with a password by setting the `MYSQL_USER` and `MYSQL_PASSWORD` environment variables.  A Secret can hold more than one key/value pair, so we can create a single Secret to hold both strings.  As a bonus, by using `kubectl create secret`, we can let Kubernetes mess with base64 for us, so we don't have to.

```
$ kubectl create secret generic mariadb-user-creds \
      --from-literal=MYSQL_USER=kubeuser\
      --from-literal=MYSQL_PASSWORD=kube-still-rocks
secret/mariadb-user-creds created
```

Note the use of `--from-literal`.  That sets the key name and the value all in one.  We can pass as many `--from-literal` arguments as needed, to create one or more key/value pairs in the secret.

Validate that the username and password were created and stored correctly with the `kubectl get secrets` command, again:

```
# Get the username
$ kubectl get secret mariadb-user-creds -o jsonpath='{.data.MYSQL_USER}' | base64 --decode -
kubeuser

# Get the password
$ kubectl get secret mariadb-user-creds -o jsonpath='{.data.MYSQL_PASSWORD}' | base64 --decode -
kube-still-rocks
```

## ConfigMaps

ConfigMaps are similar to Secrets.  They can be created in the same ways, and can be shared in the containers the same ways.  The only big difference between them is the base64 encoding obfuscation.  ConfigMaps are intended to non-sensitive data - configuration data - like config files and environment variables, and are a great way to create customized running services from generic container images.

### Create a ConfigMap

ConfigMaps can be created the same ways Secrets are.  A YAML representation of the ConfigMap can be written manually and loaded it into Kubernetes, or the `kubectl create configmap` command can be used to create it from the command line.  In the next example, we'll create a ConfigMap using the latter method, but this time, instead of passing literal strings as we did with `--from-literal=<key>=<string>` for the Secret above, we'll create a ConfigMap from an existing file - a MySQL config intended for `/etc/mysql/conf.d` in the container. For this exercise, we will override the "max_allowed_packet" setting for MariaDB, set to 16M by default, with this config file.

First, create a file named `max_allowed_packet.cnf` with the following content:

```
[mysqld]
max_allowed_packet = 64M
```

This will override the default setting in the my.cnf file and set "max_allowed_packet" to 64M.

Once the file is created, we can create a ConfigMap named "mariadb-config" using the `kubectl create configmap` command that contains the file:

```
$ kubectl create configmap mariadb-config --from-file=max_allowed_packet.cnf
configmap/mariadb-config created
```

Just like Secrets, ConfigMaps store one or more key/value pairs in their "Data" hash of the object.  By default, using `--from-file=<filename>` as we did above, the contents of the file will be stored as the value, and the name of the file will be stored as the key.  This is convenient from an organization viewpoint.  However, the keyname can be explicitly set too.  For example, if we'd used `--from-file=max-packet=max_allowed_packet.cnf` when we created the ConfigMap, the key would be "max-packet" rather than the filename.  If we had multiple files to store in the ConfigMap, we could add each of them with an additional `--from-file=<filename>` argument.


### View the new ConfigMap and read the data

As already mentioned, ConfigMaps are not meant to store sensitive data, so the data is not encoded when the ConfigMap is created.  This makes it easy to view and validate the data, and each to edit it directly if desired.

Validate that the ConfigMap we just created did, in fact, get created:

```
$ kubectl get configmap mariadb-config
NAME             DATA      AGE
mariadb-config   1         9m
```

The contents of the ConfigMap can be viewed with the `kubectl describe` command.  Note that the full contents of the file is visible, and that the keyname is in fact the file name, `max_allowed_packet.cnf`.

```
$ kubectl describe cm mariadb-config
Name:         mariadb-config
Namespace:    secrets-and-configmaps
Labels:       <none>
Annotations:  <none>


Data
====
max_allowed_packet.cnf:
----
[mysqld]
max_allowed_packet = 64M

Events:  <none>
```

A ConfigMap can be edited live within Kubernetes with the `kubectl edit` command.  Doing so will open a buffer with the default editor, showing the contents of the ConfigMap as YAML.  When changes are saved, they will be immediately live in Kubernetes.  While not really the _best_ practice, it can be handy for testing things in development.

Let's say we really wanted a "max_allowed_packet" value of 32M instead of the default 16M or the 64M in the `max_allowed_packet.cnf` file.  Use `kubectl edit configmap mariadb-config` to edit the value:

```
$ kubectl edit configmap mariadb-config

# Please edit the object below. Lines beginning with a '#' will be ignored,
# and an empty file will abort the edit. If an error occurs while saving this file will be
# reopened with the relevant failures.
#
apiVersion: v1

data:
  max_allowed_packet.cnf: |
    [mysqld]
    max_allowed_packet = 32M
kind: ConfigMap
metadata:
  creationTimestamp: 2019-05-30T12:02:22Z
  name: mariadb-config
  namespace: secrets-and-configmaps
  resourceVersion: "85609912"
  selfLink: /api/v1/namespaces/secrets-and-configmaps/configmaps/mariadb-config
  uid: c83ccfae-82d2-11e9-832f-005056a1102f
```

After saving the change, verify the data has been updated:

```
# Note the '.' in max_allowed_packet.cnf needs to be escaped
$ kubectl get configmap mariadb-config -o "jsonpath={.data['max_allowed_packet\.cnf']}"

[mysqld]
max_allowed_packet = 32M
```


## Using Secrets and ConfigMaps

Secrets and ConfigMaps can be mounted as environment variables or as files within a container.  For the MariaDB container, we will need to mount the secrets as environment variables, and the ConfigMap as a file.  First, though, we need to write a Deployment for MariaDB, so we have something to work with.  Create a file named "mariadb-deployment.yaml" with the following:

```
apiVersion: apps/v1
kind: Deployment
metadata:
  labels:
    app: mariadb
  name: mariadb-deployment
spec:
  replicas: 1
  selector:
    matchLabels:
      app: mariadb
  template:
    metadata:
      labels:
        app: mariadb
    spec:
      containers:
      - name: mariadb
        image: docker.io/mariadb:10.4
        ports:
        - containerPort: 3306
          protocol: TCP
        volumeMounts:
        - mountPath: /var/lib/mysql
          name: mariadb-volume-1
      volumes:
      - emptyDir: {}
        name: mariadb-volume-1
```

This is a bare-bones Kubernetes Deployment of the offical MariaDB 10.4 image from Docker Hub.  Now, let's add our Secrets and ConfigMap.


### Adding the Secrets to the Deployment as environment variables

We have two secrets that need to be added to the Deployment:

1.  mariadb-root-password (with one key/value pair)
2.  mariadb-user-creds (with two key/value pairs)

For the mariadb-root-password secret, we will specify the secret and the key we want by adding an `env` list/array to the container spec in the Deployment, and setting the environment variable value to the value of the key in our secret.  In this case, the list contains only a single entry, for the variable `MYSQL_ROOT_PASSWORD`.

```
 env:
   - name: MYSQL_ROOT_PASSWORD
     valueFrom:
       secretKeyRef:
         name: mariadb-root-password
         key: password
```

Note that the name of the object is the name of the environment variable that is added to the container.  The `valueFrom` field defines `secretKeyRef` as the source from which the environment variable will be set; ie: it will use the value from the "password" key in the "mariadb-root-password" secret we set earlier.

Add this section to the definition for the "mariadb" container in the mariadb-deployment.yaml file.  It should look something like this:


```
 spec:
   containers:
   - name: mariadb
     image: docker.io/mariadb:10.4
     env:
       - name: MYSQL_ROOT_PASSWORD
         valueFrom:
           secretKeyRef:
             name: mariadb-root-password
             key: password
     ports:
     - containerPort: 3306
       protocol: TCP
     volumeMounts:
     - mountPath: /var/lib/mysql
       name: mariadb-volume-1
```

In this way we have explicitly set the variable to the value of a specific key from our secret.  This method can also be used with ConfigMaps by using `configMapRef` instead of `secretKeyRef`.

It is also possible to set environment variables from _all_ key/value pairs in a secret or config map, automatically using the key name as the environment variable name and the key's value as the environment variable's value.  By using `envFrom` rather than `env` in the container spec, we can set the `MYSQL_USER` and `MYSQL_PASSWORD` from the "mariadb-user-creds" secret we created earlier, all in one go:

```
 envFrom:
 - secretRef:
     name: mariadb-user-creds
```

`envFrom` is a list of sources for Kubernetes to take environment variables.  Again, we're using `secretRef`, this time to specify "mariadb-user-creds" as the source of the environment variables.  That's it!  All the keys and values in the secret will be added as environment variables in the container.

The container spec should now look like this:

```
spec:
  containers:
  - name: mariadb
    image: docker.io/mariadb:10.4
    env:
      - name: MYSQL_ROOT_PASSWORD
        valueFrom:
          secretKeyRef:
            name: mariadb-root-password
            key: password
    envFrom:
    - secretRef:
        name: mariadb-user-creds
    ports:
    - containerPort: 3306
      protocol: TCP
    volumeMounts:
    - mountPath: /var/lib/mysql
      name: mariadb-volume-1
```
