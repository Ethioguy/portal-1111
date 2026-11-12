# Privacy

The 11/11 Portal is built so that nobody, including the project's author, can see your data.

## Public edition (this website)
- **No accounts, no server, no database.** Everything you enter, including photos, is stored only in your browser on your device.
- **No analytics, ads, trackers or third-party requests.** The page loads no outside fonts or scripts, and a strict Content-Security-Policy blocks it from contacting any other website.
- **AI is your choice.** "Copy my summary" puts a summary on your clipboard. Emails, phone numbers and ID numbers are removed first. Nothing is sent anywhere unless you paste it into an AI yourself, and then that provider's privacy terms apply.
- **You control deletion.** Setup → *Delete all my data on this device* erases your entries, photos and settings. Clearing your browser data does the same.
- **Device sync without a server.** *Setup → Sync my devices* saves a file encrypted on your device (AES-256-GCM, key derived from your passphrase with PBKDF2-SHA256, 250,000 rounds). Keep it in iCloud Drive or AirDrop it; open it on your other device with the same passphrase. Where the file is stored, only scrambled data is visible. The passphrase is never stored. Photos are not included.
- **Backups are yours.** A backup contains your personal (including health-related) data. Keep it private.

## Personal edition
A separate file (`private/PERSONAL-portal.html`) adds an option to connect your own Anthropic API key. It is excluded from this repository by `.gitignore` and is meant for the owner's own device only. Requests go directly from that device to Anthropic; the key is kept in memory unless you choose to remember it on that device.

## Cover photos and demo videos

- **Cover photos (both editions, optional).** When you tap *Show suggestions*, your device asks Openverse (`api.openverse.org`) for openly licensed photos. Only the search words for that life area are sent, never your entries. The photo you pick is copied to this device and shown with its creator, license and source. You can also upload your own.
- **Demo videos (personal edition only).** Nothing loads until you tap. Videos then play from YouTube in privacy-enhanced mode (`youtube-nocookie.com`), which still sees your IP address. Your trim settings are stored on this device. The public edition contains no video embeds.

## Python AI layer (`ai/`)
Runs on your own machine against a backup file you choose. Search runs locally; the optional coach sends redacted text to the model provider you configure. Sample data in this repo is synthetic.

## Tips
- Lock your phone and computer, and don't use the app on shared devices.
- Don't post screenshots or backups that show personal entries.

General fitness guidance, not medical advice. Questions or a security concern: open an issue on GitHub without including any personal data.
