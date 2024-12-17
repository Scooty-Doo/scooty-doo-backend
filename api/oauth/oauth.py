"""
const CLIENT_ID = 'YOUR_GITHUB_CLIENT_ID';
const CLIENT_SECRET = 'YOUR_GITHUB_CLIENT_SECRET';

app.post('/auth/github/callback', async (req, res) => {
    const { code } = req.body;

    // Exchange code for access token
    const tokenResponse = await fetch('https://github.com/login/oauth/access_token', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',

        },
        body: JSON.stringify({
            client_id: CLIENT_ID,
            client_secret: CLIENT_SECRET,
            code,
        }),
    });
    const tokenData = await tokenResponse.json();
    const accessToken = tokenData.access_token;

    if (accessToken) {
        // Use this access token to fetch user details or other tasks.
        // Maybe generate a JWT and send it to the frontend for session management.
        res.json({ success: true });
    } else {
        res.json({ success: false });
    }
});
"""

import os

import httpx
from dotenv import load_dotenv
from fastapi import HTTPException

load_dotenv()


async def get_github_access_token(code: str):
    """Get the access token from the GitHub API."""
    url = "https://github.com/login/oauth/access_token"
    headers = {"Accept": "application/json"}
    data = {
        "client_id": os.getenv("GITHUB_CLIENT_ID"),
        "client_secret": os.getenv("GITHUB_CLIENT_SECRET"),
        "code": code,
        "redirect_uri": os.getenv("GITHUB_REDIRECT_URI"),
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, data=data)

    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to fetch access token")

    token_data = response.json()
    access_token = token_data.get("access_token")

    if not access_token:
        raise HTTPException(status_code=400, detail="Access token not found")

    return access_token


async def get_github_user(access_token: str):
    """Get the user details from the GitHub API."""
    url = "https://api.github.com/user"
    headers = {"Authorization": f"Bearer {access_token}"}

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)

    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to fetch user info")

    return response.json()
