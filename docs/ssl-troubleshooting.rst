SSL Certificate Troubleshooting
===============================

This guide helps you resolve SSL certificate issues when connecting to YouTrack instances with custom SSL certificates.

Common SSL Errors
------------------

Certificate Verification Failed
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Error Message:**

.. code-block:: text

   [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate

**Cause:** This error occurs when the system cannot verify the SSL certificate because it doesn't have the necessary Certificate Authority (CA) certificates.

**Solution:** Use one of the following options:

1. **Use CA Bundle (Recommended):**
   ```bash
   yt auth login --ca-bundle /path/to/ca-bundle.crt
   ```

2. **Use Certificate Chain File:**
   ```bash
   yt auth login --cert-file /path/to/full-chain.pem
   ```

3. **Disable SSL Verification (Not Recommended):**
   ```bash
   yt auth login --no-verify-ssl
   ```

Understanding Certificate Types
-------------------------------

Server Certificate vs CA Bundle
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- **Server Certificate**: The certificate presented by the YouTrack server (e.g., for \*.mydohc.com)
- **CA Bundle**: A file containing Certificate Authority certificates needed to verify the server certificate
- **Certificate Chain**: A file containing both the server certificate and the CA certificates

For SSL verification to work, you need the CA certificates, not just the server certificate.

Creating a CA Bundle
--------------------

For DigiCert/GeoTrust Certificates
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If your certificate is issued by DigiCert or GeoTrust (like the example certificate), create a CA bundle containing the intermediate and root certificates:

1. **Download the CA certificates:**
   - GeoTrust TLS RSA CA G1 (intermediate)
   - DigiCert Global Root CA (root)

2. **Create the CA bundle file:**
   ```bash
   cat intermediate.crt root.crt > ca-bundle.crt
   ```

3. **Use with YouTrack CLI:**
   ```bash
   yt auth login --ca-bundle /path/to/ca-bundle.crt
   ```

For Self-Signed Certificates
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. **Create a CA bundle with your root CA:**
   ```bash
   cp your-root-ca.crt ca-bundle.crt
   ```

2. **Use with YouTrack CLI:**
   ```bash
   yt auth login --ca-bundle /path/to/ca-bundle.crt
   ```

Environment Variables
---------------------

You can also set SSL configuration via environment variables:

```bash
export YOUTRACK_CA_BUNDLE=/path/to/ca-bundle.crt
export YOUTRACK_CERT_FILE=/path/to/cert-chain.pem
export YOUTRACK_VERIFY_SSL=true
```

Testing SSL Configuration
-------------------------

Test Certificate File
~~~~~~~~~~~~~~~~~~~~~

Verify that your certificate file is valid:

```bash
openssl x509 -in certificate.pem -text -noout
```

Test Connection
~~~~~~~~~~~~~~~

Test SSL connection to your YouTrack instance:

```bash
openssl s_client -connect your.youtrack.domain:443 -CAfile /path/to/ca-bundle.crt
```

Common Issues and Solutions
---------------------------

Certificate Chain Issues
~~~~~~~~~~~~~~~~~~~~~~~~

**Problem:** "unable to get local issuer certificate"
**Solution:** Ensure your CA bundle contains all intermediate certificates in the chain.

Wrong File Type
~~~~~~~~~~~~~~~

**Problem:** Certificate verification still fails with correct files
**Solution:** Ensure certificate files are in PEM format, not DER or other formats.

Missing Root CA
~~~~~~~~~~~~~~~

**Problem:** Chain verification works partially but still fails
**Solution:** Add the root CA certificate to your CA bundle.

Best Practices
--------------

1. **Use CA bundles** instead of disabling SSL verification
2. **Keep certificates updated** before expiration
3. **Store certificates securely** with appropriate file permissions
4. **Test certificate configuration** before deploying to production
5. **Use absolute paths** when specifying certificate files

Example Configuration
---------------------

Complete SSL setup example:

.. code-block:: bash

   # 1. Create CA bundle with intermediate and root certificates
   cat geotrust-tls-rsa-ca-g1.crt digicert-global-root-ca.crt > youtrack-ca-bundle.crt

   # 2. Set proper file permissions
   chmod 644 youtrack-ca-bundle.crt

   # 3. Login with CA bundle
   yt auth login \
       --base-url https://your.youtrack.domain \
       --ca-bundle /path/to/youtrack-ca-bundle.crt

   # 4. Verify connection
   yt projects list

Getting Help
------------

If you continue to experience SSL certificate issues:

1. Check the certificate chain with OpenSSL tools
2. Verify that all intermediate certificates are included
3. Ensure certificate files are readable by the CLI
4. Consider using ``--no-verify-ssl`` temporarily for testing (disable for production)

For additional support, check the troubleshooting section in the main documentation.
