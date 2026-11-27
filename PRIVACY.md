# Privacy

Portal 11 is built so that nobody, including the project's author, can see your data.

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

## Watch import

The optional iPhone Shortcut opens the app with your distance and minutes in the part of the link after `#`. Browsers never send that part to any server, including GitHub Pages. The app shows the numbers and saves them on this device only when you tap Save.

## Python AI layer (`ai/`)
Runs on your own machine against a backup file you choose. Search runs locally; the optional coach sends redacted text to the model provider you configure. Sample data in this repo is synthetic.

## Tips
- Lock your phone and computer, and don't use the app on shared devices.
- Don't post screenshots or backups that show personal entries.

General fitness guidance, not medical advice. Questions or a security concern: open an issue on GitHub without including any personal data.

## Data and AI practice

- **One network request** loads the app: the page itself. No analytics, no trackers, no third-party fonts or scripts.
- **No AI in the public build.** `tools/build_editions.py` asserts that the published edition contains no AI connection code, no API-key handling and no third-party embeds, and CI runs that build on every push. The optional coach exists only in a personal edition that is never published.
- **Two optional outbound calls**, both started by you: searching Openverse sends your search words only; playing a publisher's track streams it from their server, which sees your IP as any website would. Neither sends anything you have typed, and no audio or image is stored in this repository.
- **Architecture, not policy.** There is no server, so there is no copy of your data to breach, subpoena or sell. The cost is that nothing syncs and nothing can be recovered for you — which is why the app asks you to back up rather than pretending the problem away.
- **Not assessed against any named AI governance framework.** The claims above are checkable in the source; that is the whole of the assurance offered.
