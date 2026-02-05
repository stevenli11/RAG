# How to Create GitHub Release V1.1.0

This guide explains how to create a GitHub Release for version 1.1.0.

## Option 1: Using GitHub Web Interface (Recommended)

1. **Navigate to Releases**
   - Go to the repository: https://github.com/stevenli11/RAG
   - Click on "Releases" in the right sidebar (or go to `/releases`)

2. **Create New Release**
   - Click "Draft a new release" button

3. **Configure Release**
   - **Tag version**: `v1.1.0` (create new tag)
   - **Target**: Select the branch with the latest changes
   - **Release title**: `V1.1.0 - OCR Support & Intelligent Question Classification`
   - **Description**: Copy content from `RELEASE_NOTES_V1.1.md`

4. **Publish**
   - Click "Publish release"

## Option 2: Using GitHub CLI

```bash
gh release create v1.1.0 \
  --title "V1.1.0 - OCR Support & Intelligent Question Classification" \
  --notes-file RELEASE_NOTES_V1.1.md
```

## Notes

- Tag should be `v1.1.0` (with 'v' prefix)
- This release documents features from PR #12
