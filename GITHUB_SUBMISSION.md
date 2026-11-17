# GitHub Repository and Teacher Submission

The instructor requires the **source code pushed to GitHub**, the **repository link emailed together with group information** by **Thursday, November 19, 2026, 11:59 PM**, and a **class presentation November 21, 2026**.

The files supplied in this folder are ready to publish, but **the repository has not been created/pushed and the email has not been sent**. A group member must perform those account-specific actions.

## Recommended GitHub method (web browser)

1. Sign in to github.com with a group member's GitHub account.
2. Create a new public repository named `INFO301-Project3-CampusCart` (or the name the group chooses).
3. Upload **all files and folders** from inside this project folder (`app.py`, `README.md`, `tests`, `data`, `docs`, etc.). Preserve the folder structure. Do not upload only the ZIP.
4. Check that `app.py`, four `.csv` files, `README.md`, `TEST_CHECKLIST.md`, and `tests/test_app.py` are visible in the repository.
5. Copy the repository's full HTTPS link (it will look like `https://github.com/YOUR-ACCOUNT/INFO301-Project3-CampusCart`).
6. Email the link with your course, group name/number, project title, and member names / student IDs to **gdolokelen@gmail.com** before the deadline.

## Alternate terminal commands (only after creating your empty GitHub repository)

```bash
git init
git add .
git commit -m "INFO 301 Project 3 CampusCart final submission"
git branch -M main
git remote add origin https://github.com/YOUR-ACCOUNT/INFO301-Project3-CampusCart.git
git push -u origin main
```

Replace `YOUR-ACCOUNT` with your real GitHub username. GitHub authentication is required for the push.

## Suggested submission email wording

**Subject:** INFO 301 Semester 2 Final Project - Project 3 - [Group Name]

Dear Lecturer,

Please find our group submission for INFO 301, Project 3: E-commerce Application (CampusCart).

GitHub repository: [paste the actual URL here]

Group: [group name/number]  
Members and Student IDs: [insert complete details]

The repository contains the Python source code, fictional CSV datasets, README instructions, automated tests, test checklist, and presentation documentation.

Thank you.

[Group representative's name]

## Before clicking Send

- Confirm the repository URL opens and shows the actual Python files.
- Confirm the CSV example data is included and contains 30+ records.
- Run the project one more time from a fresh clone/download.
- Send before **11:59 PM on November 19, 2026** (do not rely on last-minute uploads).
