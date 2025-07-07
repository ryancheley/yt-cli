Security Features
================

YouTrack CLI includes comprehensive security enhancements to protect user credentials and provide audit capabilities for enterprise environments.

Overview
--------

The security features include:

- **Command Audit Logging**: Track all CLI commands with timestamps
- **Credential Encryption**: Secure storage of tokens and credentials
- **Token Expiration Warnings**: Proactive alerts before tokens expire
- **Sensitive Data Masking**: Automatic masking of credentials in output and logs

Command Audit Logging
--------------------

All CLI commands are automatically logged with timestamps for security auditing and compliance purposes.

**Features:**

- Logs command names, arguments, timestamps, and execution status
- Automatically masks sensitive information (tokens, passwords, API keys)
- Configurable storage limits (default: 1000 entries)
- JSON export capability for integration with external systems

**Usage:**

View recent audit entries::

    yt security audit

View more entries::

    yt security audit --limit 100

Export as JSON::

    yt security audit --format json

Clear audit log::

    yt security clear-audit

**Configuration:**

Audit logging can be disabled using the ``--secure`` flag::

    yt --secure issues list

This prevents command logging while maintaining other security features.

Credential Encryption
--------------------

Credentials are encrypted at rest using industry-standard encryption and the system keyring where available.

**Features:**

- AES encryption using the ``cryptography`` library
- System keyring integration (Keychain on macOS, Credential Manager on Windows, Secret Service on Linux)
- Automatic fallback to encrypted file storage
- Secure key generation and management

**Storage Locations:**

The CLI attempts to store credentials in the following order:

1. **System Keyring** (most secure) - Uses OS-provided credential storage
2. **Encrypted File** (fallback) - ``~/.local/share/youtrack-cli/`` with encryption
3. **Plain Text File** (legacy) - ``~/.config/youtrack-cli/.env`` for compatibility

**Usage:**

Credentials are automatically encrypted when using ``yt auth login``::

    yt auth login

The system will indicate the storage method used:

- ✅ Green: Stored securely in keyring
- ⚠️ Yellow: Stored in encrypted file (keyring unavailable)

**Environment Variables:**

For CI/CD environments, you can disable keyring and use environment variables::

    export YOUTRACK_BASE_URL="https://company.youtrack.cloud"
    export YOUTRACK_TOKEN="your-api-token"

Token Expiration Management
-------------------------

The CLI proactively monitors token expiration and provides warnings before tokens expire.

**Features:**

- Automatic expiration checking on credential load
- Configurable warning period (default: 7 days)
- Color-coded status indicators
- Manual token status checking

**Usage:**

Check current token status::

    yt security token-status

The output will show:

- 🟢 **Valid**: Token is current and not expiring soon
- 🟡 **Expiring**: Token expires within the warning period
- 🔴 **Expired**: Token has expired and needs renewal
- ⚪ **Unknown**: Expiration date not available

**Setting Token Expiry:**

When creating tokens in YouTrack, note the expiration date. The CLI will automatically detect JWT token expiration where possible.

SSL Verification Warnings
-------------------------

The CLI monitors SSL certificate verification settings and issues security warnings when SSL verification is disabled.

**Features:**

- Automatic detection of SSL verification bypass via environment variables
- Security warnings displayed when SSL verification is disabled
- Audit logging of SSL configuration changes for compliance tracking
- Clear messaging about security implications

**Usage:**

By default, SSL verification is enabled and the CLI will verify certificates for all HTTPS connections to YouTrack::

    # SSL verification enabled (default, secure)
    yt issues list

To disable SSL verification (for development environments only), set the environment variable::

    # SSL verification disabled (INSECURE - development only)
    export YOUTRACK_VERIFY_SSL=false
    yt issues list

When SSL verification is disabled, you will see a security warning::

    ⚠️  SSL verification is DISABLED. This is insecure and should only be used in development.

**Security Implications:**

Disabling SSL verification exposes your connection to man-in-the-middle attacks where:

- Attackers can intercept and read your API tokens and data
- Malicious actors can modify requests and responses
- Your YouTrack credentials and data may be compromised

**Audit Logging:**

All SSL configuration changes are automatically logged in the audit trail::

    yt security audit

This includes entries for:

- SSL verification status (enabled/disabled)
- Environment variable values
- Timestamps of configuration changes

**Best Practices:**

1. **Never disable SSL verification in production environments**
2. Only use ``YOUTRACK_VERIFY_SSL=false`` for local development with self-signed certificates
3. Monitor audit logs for unexpected SSL verification changes
4. Use proper CA-signed certificates in all production environments
5. Consider using organizational certificate authorities for internal systems

Sensitive Data Masking
---------------------

All output and logs automatically mask sensitive information to prevent credential exposure.

**Masked Patterns:**

- API tokens and bearer tokens
- Passwords and passphrases
- API keys and secrets
- Authorization headers

**Example Output:**

Before masking::

    Authorization: Bearer perm:abc123.def456.ghi789
    token=secret_api_key_here

After masking::

    Authorization: Bearer ***MASKED***
    token=***MASKED***

Security Best Practices
----------------------

**For Individual Users:**

1. **Use System Keyring**: Allow the CLI to use your system's credential manager
2. **Monitor Token Expiry**: Regularly check ``yt security token-status``
3. **Review Audit Logs**: Periodically check ``yt security audit`` for unexpected activity
4. **Secure Environment**: Keep your system updated and use endpoint protection

**For Enterprise Environments:**

1. **Centralized Audit Collection**: Export audit logs to SIEM systems::

       yt security audit --format json > audit-export.json

2. **Token Lifecycle Management**:

   - Set appropriate token expiration periods
   - Implement token rotation policies
   - Monitor for expired tokens across teams

3. **Access Control**:

   - Use principle of least privilege for token permissions
   - Regularly review and revoke unused tokens
   - Implement approval workflows for sensitive operations

4. **Compliance Integration**:

   - Configure automated audit log collection
   - Set up alerts for failed authentication attempts
   - Maintain audit trails for compliance reporting

**For CI/CD Pipelines:**

1. **Environment Variables**: Use secure environment variable storage::

       # In your CI/CD system
       YOUTRACK_BASE_URL=https://company.youtrack.cloud
       YOUTRACK_TOKEN=ci_token_here

2. **Secure Flag**: Use ``--secure`` to prevent logging in automated environments::

       yt --secure issues create PROJECT-123 "Automated issue"

3. **Token Scoping**: Create dedicated CI tokens with minimal required permissions

4. **Secret Rotation**: Implement regular token rotation for automated systems

Configuration Options
--------------------

Security features can be configured through environment variables or the configuration file.

**Environment Variables:**

.. code-block:: bash

    # Disable audit logging
    export YT_AUDIT_LOGGING=false

    # Disable credential encryption
    export YT_CREDENTIAL_ENCRYPTION=false

    # Disable token expiration warnings
    export YT_TOKEN_WARNINGS=false

    # Set custom warning period (days)
    export YT_TOKEN_WARNING_DAYS=14

    # Set audit log size limit
    export YT_AUDIT_MAX_ENTRIES=2000

**Configuration File:**

Add to ``~/.config/youtrack-cli/.env``::

    YT_AUDIT_LOGGING=true
    YT_CREDENTIAL_ENCRYPTION=true
    YT_TOKEN_WARNINGS=true
    YT_TOKEN_WARNING_DAYS=7
    YT_AUDIT_MAX_ENTRIES=1000

Troubleshooting
--------------

**Keyring Issues:**

If keyring storage fails:

1. Install keyring backends::

       # Linux
       sudo apt-get install gnome-keyring python3-keyring

       # macOS (usually available by default)
       pip install keyring

       # Windows (usually available by default)
       pip install keyring

2. Check keyring status::

       python -c "import keyring; print(keyring.get_keyring())"

3. Fall back to file storage if needed - the CLI will automatically handle this

**Audit Log Issues:**

If audit logging fails:

1. Check permissions on log directory::

       ls -la ~/.local/share/youtrack-cli/

2. Manually create directory if needed::

       mkdir -p ~/.local/share/youtrack-cli/

3. Clear corrupted audit log::

       yt security clear-audit --force

**Token Expiration Issues:**

If token warnings are incorrect:

1. Update token with correct expiry::

       yt auth token --update

2. Check system clock synchronization
3. Verify token format and YouTrack version compatibility

Security Considerations
---------------------

**Limitations:**

- Keyring availability varies by system configuration
- Audit logs are stored locally (consider centralized collection for enterprises)
- Token expiration detection depends on YouTrack API and token format
- File permissions rely on operating system security

**Recommendations:**

- Regularly backup encrypted credential files
- Monitor system security updates
- Use dedicated service accounts for automation
- Implement network-level security controls
- Consider using VPN or private networks for YouTrack access

**Compliance:**

The security features support various compliance frameworks:

- **SOC 2**: Audit logging and access controls
- **ISO 27001**: Information security management
- **GDPR**: Data protection and audit trails
- **PCI DSS**: Secure credential handling

For specific compliance requirements, consult with your security team to configure appropriate controls and monitoring.
