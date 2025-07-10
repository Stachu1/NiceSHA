# 🔑 Nice SHA

This Python script brute-forces the timestamp of the latest commit at `HEAD` to find a **"nicer-looking" SHA-1 hash**, such as one starting with `12345` or `FFFFF`.  
It works by iteratively adjusting the Unix timestamp of the commit and predicting what the resulting SHA will be — **without making actual changes** until a better match is found.

---

## ⚙️ Features

- Computes the potential SHA-1 of a commit by simulating timestamp changes
- Searches for a target prefix (e.g., `12345`, `deadbeef`, `abcdef`)
- Shows real-time progress and hash rate in kH/s
- Applies the best timestamp match upon pressing Enter
- No changes are committed until confirmed

---

## 🚀 Usage

```bash
python nice_sha.py [target_prefix]
```

- `target_prefix`: Desired starting sequence in the SHA (e.g., `abcd`, `0000`, `face`, etc.)
- Example:
  ```bash
  python nice_sha.py 12345
  ```

Once started, the script will:
- Search for a better SHA-1 by modifying only the **commit timestamp**
- Continuously display the best SHA found so far and the search speed
- Wait for you to press `[Enter]` to apply the best match via `git commit --amend`

---

## 🧪 Example Output

```
🔹1234abcd - 1720617543 | ⚡42.38 kH/s
🔹12345fff - 1720617511 | ⚡48.12 kH/s
  Applying lowest SHA found... Done!
  Exiting cleanly
```

---

## 📁 What It Does

- Retrieves the current `HEAD` commit data (tree, parent, author, committer, message)
- Simulates timestamp changes and re-generates the commit's content hash
- Finds the timestamp that results in the closest match to the target
- Uses `git commit --amend --date="..."` to apply it safely
