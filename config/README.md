# Configuration Setup

This directory contains configuration files for the Logistics AI Response System.

## 🔒 Sensitive Configuration Files

The following files contain sensitive information and are **NOT** tracked in Git:

- `sales_team.json` - Contains real sales team contact information
- `forwarders.json` - Contains real forwarder contact information  
- `email_config.json` - Contains email server credentials

## 🚀 Setup Instructions

### 1. Copy Template Files

```bash
# Copy the template files to create your actual configuration
cp config/sales_team.template.json config/sales_team.json
cp config/forwarders.template.json config/forwarders.json
cp config/email_config.template.json config/email_config.json
```

### 2. Customize Configuration Files

Edit each file with your actual data:

#### `sales_team.json`
- Replace placeholder names, emails, and phone numbers
- Add your actual sales team members
- Update specializations and assignment rules

#### `forwarders.json`
- Add your actual forwarder contacts
- Update email addresses and company information
- Include real contact person details

#### `email_config.json`
- Add your email server credentials
- Configure SMTP settings
- Set up authentication tokens

### 3. Verify Configuration

Run the system to ensure all configurations are working:

```bash
python3 -c "
import json
# Test sales team
with open('config/sales_team.json', 'r') as f:
    sales_data = json.load(f)
print(f'✅ Sales team: {len(sales_data[\"sales_team\"])} members')

# Test forwarders
with open('config/forwarders.json', 'r') as f:
    forwarder_data = json.load(f)
print(f'✅ Forwarders: {len(forwarder_data[\"forwarders\"])} contacts')
"
```

## 🔐 Security Notes

- Never commit real configuration files to Git
- Keep your configuration files secure
- Use environment variables for sensitive data when possible
- Regularly update contact information

## 📋 File Structure

```
config/
├── README.md                    # This file
├── sales_team.template.json     # Template for sales team
├── forwarders.template.json     # Template for forwarders
├── email_config.template.json   # Template for email config
├── config.json                  # General configuration (tracked)
├── settings.py                  # Settings module (tracked)
└── config_loader.py             # Configuration loader (tracked)
```

## 🆘 Troubleshooting

If you encounter issues:

1. **Missing files**: Copy the template files first
2. **JSON errors**: Validate your JSON syntax
3. **Permission errors**: Check file permissions
4. **Git tracking**: Ensure sensitive files are in .gitignore 