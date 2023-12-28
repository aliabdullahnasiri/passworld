# Passworld - Command-Line Password Manager

Passworld is a secure and efficient command-line password manager designed to simplify password management and enhance security. It offers a range of features to help users generate, store, and manage their passwords seamlessly.

## Features

- **Secure Storage:** Passwords are encrypted and stored securely to ensure the confidentiality of sensitive information.

- **Password Generation:** Generate strong and random passwords with customizable length.

- **Search and Display:** Easily search for and display password entries with options for limiting results and setting timeouts.

- **Clipboard Integration:** Copy passwords to the clipboard for quick and convenient use.

- **Import and Export:** Import and export passwords using CSV files to facilitate easy migration and backup.

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/passworld.git
   ```
2. Navigate to the project directory:

   ```
   cd passworld
   ```
3. Run the Passworld manager:

   ```
   python passworld.py
   ```

## Usage

### List Passwords
   ```bash
   python passworld.py list-passwords
   ```
List and display password entries with various options like search, limit, and timeout.

### Add Password
   ```bash
   python passworld.py add-password
   ```
Add a new password entry with prompts for name, website, username, password, and optional notes.

### Generate Password
   ```bash
   python passworld.py generate-password
   ```
Generate a random password with options for length and clipboard integration.

### Export Passwords
   ```bash
   python passworld.py export-passwords output.csv
   ```
Export password entries to a CSV file for backup or migration.

### Import Passwords
   ```bash
   python passworld.py import-passwords input.csv
   ```
Import password entries from a CSV file.

### Delete Password
   ```bash
   python passworld.py delete-password --password-id <password_id>
   ```
Delete a password entry by specifying the password ID with an optional force flag for confirmation.

### Edit Password
   ```bash
   python passworld.py edit-password --password-id <password_id>
   ```
Edit a password entry by specifying the password ID.

## Dependencies
   - Python 3
   - Click
   - Pyperclip
   - Rich

## Report Bug

If you encounter any issues, bugs, or unexpected behavior while using Passworld, please help us improve by reporting it. To report a bug, follow these steps:

1. **Check for Existing Issues:** Before reporting a new issue, check the [existing issues](https://github.com/aliabdullahnasiri/passworld/issues) to see if someone has already reported a similar problem.

2. **Create a New Issue:** If you don't find an existing issue that matches your problem, [create a new issue](https://github.com/aliabdullahnasiri/passworld/issues/new). Clearly describe the issue, including steps to reproduce it and any error messages you received.

3. **Include Relevant Information:**
   - Mention the version of Passworld you are using.
   - Specify your operating system (e.g., Windows, macOS, Linux).
   - Provide any additional context that might be helpful in understanding and reproducing the issue.

4. **Label the Issue:** Apply relevant labels to your issue, such as "bug" or any other applicable label.

5. **Be Responsive:** If there are follow-up questions or requests for clarification, please respond promptly to help us investigate and resolve the issue.

We appreciate your help in improving Passworld! 🙌


## License
This project is licensed under the GPL-2.0 License - see the [LICENSE](https://github.com/aliabdullahnasiri/passworld/#GPL-2.0-1-ov-file) file for details.
