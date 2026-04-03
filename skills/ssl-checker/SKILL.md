# SSL Certificate Checker

**Description:** Check SSL/TLS certificates - expiration, validity, issuer, grade, and details.

**Commands:**
- `check <domain>` - Check SSL certificate
- `expiry <domain>` - Check expiration date
- `grade <domain>` - Get SSL grade
- `details <domain>` - Full certificate details
- `compare <domain1> <domain2>` - Compare certificates

**Usage:**
```bash
python handler.py check google.com
python handler.py expiry github.com
```
